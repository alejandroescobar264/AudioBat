from flask import Flask, request, jsonify, send_from_directory
import zipfile
from modelo.senial import SenialAudioWAV
from procesador.procesador import HighPassFilter, LowPassFilter, Segmenter
from visualizador.visualizador import Visualizador
from reportador.reportador import JSONReportGenerator
from pathlib import Path

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append("/Audiobat/src/audiobat")

app = Flask(__name__)


app = Flask(__name__)

# Directorio temporal para guardar el archivo subido
UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Crea el directorio si no existe

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    if 'audio_file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    # Guardar el archivo en el directorio temporal
    file = request.files['audio_file']
    filename = file.filename  # Asegurar el nombre del archivo
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    # Procesar el audio
    process_audio(file_path)

    # Crear el archivo ZIP con los resultados
    with zipfile.ZipFile('results.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('Salidas'):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), 'Salidas'))

    return jsonify({'status': 'success', 'message': 'Audio processed and results zipped'})


@app.route('/process_audio', methods=['POST'])
def process_audio():
    data = request.json
    file_path = Path(data['file_path'])
    start_time = data.get('start_time', 0)
    duration = data.get('duration', 10)
    hp_cutoff = data.get('high_pass_cutoff', 2500)
    lp_cutoff = data.get('low_pass_cutoff', 5000)

    # Cargar la señal de audio
    senial_audio = SenialAudioWAV(file_path)

    # Procesar la señal
    segmenter = Segmenter(senial_audio, start_time, duration)
    segmenter.process()
    segment = segmenter.get_processed_data()

    highpass = HighPassFilter(segment, hp_cutoff)
    highpass.process()
    lowpass = LowPassFilter(highpass.get_processed_data(), lp_cutoff)
    lowpass.process()

    # Generar gráficos y reporte
    output_dir = Path('Salidas') / file_path.stem
    visualizador = Visualizador(output_dir, file_path.stem)
    visualizador.plot_audio(segment)
    report_generator = JSONReportGenerator(output_dir)
    report_generator.generate_report(senial_audio, segmenter, highpass, lowpass)

    return jsonify({"status": "success", "message": "Audio processed successfully"})



if __name__ == '__main__':
    app.run()

# Ruta para descargar el archivo ZIP
@app.route('/download_results')
def download_results():
    try:
        return send_from_directory('', 'results.zip', as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': 'Results ZIP not found'}), 404
