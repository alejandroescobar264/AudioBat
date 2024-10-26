from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, url_for
import zipfile
import os
import sys
import threading  # Para manejar el progreso de manera concurrente

# Importa tus módulos según tu estructura de proyecto
from modelo.senial import SenialAudioWAV
from procesador.procesador import DCRemover, HighPassFilter, LowPassFilter, Segmenter, FFTProcessor, EventProcessor
from visualizador.visualizador import Visualizador
from reportador.reportador import JSONReportGenerator

app = Flask(__name__)

# Directorios de trabajo
UPLOAD_FOLDER = '/tmp/uploads'
OUTPUT_FOLDER = '/tmp/output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Variable global para almacenar el progreso
processing_progress = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'audio_file' not in request.files:
        return jsonify({'error': 'No se encontró el archivo'}), 400
    file = request.files['audio_file']
    filename = file.filename
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)
    
    # Crear subdirectorio de salida
    output_subfolder = os.path.join(OUTPUT_FOLDER, os.path.splitext(filename)[0])
    os.makedirs(output_subfolder, exist_ok=True)

    # Inicializar el progreso
    processing_progress[filename] = {'status': 'processing', 'progress': 0}
    
    # Procesar el archivo en un hilo separado
    threading.Thread(target=process_audio, args=(file_path, filename, output_subfolder)).start()
    
    return jsonify({'message': 'Archivo subido y procesamiento iniciado', 'filename': filename})

@app.route('/progress/<filename>', methods=['GET'])
def get_progress(filename):
    progress = processing_progress.get(filename, {'status': 'not found', 'progress': 0})
    return jsonify(progress)

def process_audio(file_path, filename, output_dir, start_time=0, duration=10, hp_cutoff=2500, lp_cutoff=5000):
    senial_audio = SenialAudioWAV(file_path)
    
    dc_remover = DCRemover(senial_audio)
    dc_remover.process()
    senial_audio_dc_remove = dc_remover.get_processed_data()
    
    segmenter = Segmenter(senial_audio_dc_remove, start_time, duration)
    segmenter.process()
    segment = segmenter.get_processed_data()

    # Update progress
    processing_progress[filename]['progress'] = 20  # Progreso del 20% después del segmentado
    

    highpass = HighPassFilter(segment, hp_cutoff)
    highpass.process()
    processing_progress[filename]['progress'] = 40  # Progreso del 40% después del filtrado

    lowpass = LowPassFilter(highpass.get_processed_data(), lp_cutoff)
    lowpass.process()
    processing_progress[filename]['progress'] = 60  # Progreso del 60% después del filtrado

    segmento_senial_filtrada = lowpass.get_processed_data()

    # Detección de eventos
    energy_threshold = 1e+6
    min_duration_ms = 20 
    focus_freq = (1500, 5000)
    
    event_processor = EventProcessor(segmento_senial_filtrada, energy_threshold, min_duration_ms, focus_freq, output_dir, filename)
    event_processor.process()
    processing_progress[filename]['progress'] = 80  # Progreso del 80% después de la detección de eventos

    # Procesamiento FFT
    fft_processor = FFTProcessor(segmento_senial_filtrada)
    magitudes, frecuencia, frecuencia_muestreo = fft_processor.process()
    
    # Visualización y reporte
    visualizador = Visualizador(output_dir, filename)
    visualizador.plot_audio(senial_audio)
    visualizador.plot_audio_segment_filtrado(segment, segmento_senial_filtrada, start_time)
    visualizador.plot_audio_segment_and_spectrogram(segmento_senial_filtrada, start_time, focus_freq=(1500, 5000))
    visualizador.plot_spectrogram_events_complete(event_processor)
    visualizador.plot_spectrum(magitudes, frecuencia, frecuencia_muestreo)

    # Generación de reporte JSON
    report_generator = JSONReportGenerator(output_dir, filename)
    report_generator.generate_report(senial_audio, segmenter, highpass, lowpass, event_processor)

    # Marcar el progreso como completado
    processing_progress[filename]['status'] = 'completed'
    processing_progress[filename]['progress'] = 100

@app.route('/download/<string:audio_filename>')
def download(audio_filename):
    zip_filename = os.path.splitext(audio_filename)[0] + '.zip'
    zip_path = os.path.join(OUTPUT_FOLDER, zip_filename)
    
    # Comprime el directorio de salida en un archivo ZIP
    output_subfolder = os.path.join(OUTPUT_FOLDER, os.path.splitext(audio_filename)[0])
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(output_subfolder):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, output_subfolder))
    
    try:
        return send_from_directory(OUTPUT_FOLDER, zip_filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': 'Archivo ZIP no encontrado'}), 404


@app.route('/available_files', methods=['GET'])
def available_files():
    files = os.listdir(OUTPUT_FOLDER)
    # Filtra solo los archivos ZIP
    zip_files = [f for f in files if f.endswith('.zip')]
    return jsonify(zip_files)




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
