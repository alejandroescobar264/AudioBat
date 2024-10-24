from flask import Flask, request, jsonify
from modelo.senial import SenialAudioWAV
from procesador.procesador import HighPassFilter, LowPassFilter, Segmenter
from visualizador.visualizador import Visualizador
from reportador.reportador import PDFReportGenerator
from pathlib import Path

app = Flask(__name__)

@app.route('/process_audio', methods=['POST'])
def process_audio():
    data = request.json
    file_path = Path(data['Audio/Grabaciones/AR1/AR1ecAR1303712_20240918_012907.wav'])
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
    report_generator = PDFReportGenerator(output_dir)
    report_generator.generate_report(senial_audio, segmenter, highpass, lowpass, None)

    return jsonify({"status": "success", "message": "Audio processed successfully"})

if __name__ == '__main__':
    app.run(debug=True)
