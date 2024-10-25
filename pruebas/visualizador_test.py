import unittest
from unittest.mock import MagicMock
import numpy as np
from pathlib import Path

import sys
import os
# Añade el directorio raíz del proyecto al PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from visualizador.visualizador import Visualizador
from modelo.senial import SenialAudioWAV
from pruebas.utils import generar_senial_senoidal, crear_senial_prueba


class TestVisualizador(unittest.TestCase):
    
    def setUp(self):
        # Crear una señal de prueba en un archivo WAV temporal
        self.frecuencia_senal = 440  # Frecuencia en Hz
        self.duracion_senal = 2  # Duración en segundos
        self.frecuencia_muestreo = 44100  # Frecuencia de muestreo en Hz
        self.ruta_archivo = "test_audio.wav"
        self.datos = generar_senial_senoidal(self.frecuencia_senal, self.duracion_senal, self.frecuencia_muestreo)

        # Generar señal de prueba
        crear_senial_prueba(self.ruta_archivo, self.frecuencia_senal, self.duracion_senal, self.frecuencia_muestreo)
        
        # Crear una instancia de SenialAudioWAV
        self.senial = SenialAudioWAV(self.ruta_archivo)
        
        # Inicializar Visualizador
        self.output_dir = Path("Salidas")
        self.output_dir.mkdir(exist_ok=True)
        self.visualizador = Visualizador(self.output_dir, "test_audio")

    def tearDown(self):
        # Eliminar archivos de prueba después de cada test
        if os.path.exists(self.ruta_archivo):
            os.remove(self.ruta_archivo)

        # Limpiar los archivos de salida si existen
        for output_file in self.output_dir.glob("*.png"):
            os.remove(output_file)

    def test_plot_audio(self):
        # Prueba de la función plot_audio
        self.visualizador.plot_audio(self.senial)
        # Comprobar si se ha creado el archivo de salida
        output_file = self.output_dir / "test_audio_complete_signal.png"
        self.assertTrue(output_file.exists(), "El archivo de salida no fue creado.")

    def test_plot_spectrum(self):
        # Prueba de la función plot_spectrum
        magnitudes = np.random.rand(100)  # 100 puntos de magnitud
        freqs = np.linspace(0, 22050, 100)  # Frecuencias de 0 a 22.05 kHz
        fs = 44100  # Frecuencia de muestreo
        self.visualizador.plot_spectrum(magnitudes, freqs, fs)
        # Comprobar si se ha creado el archivo de salida
        output_file = self.output_dir / "test_audio_frequency_spectrum.png"
        self.assertTrue(output_file.exists(), "El archivo de salida no fue creado.")

    def test_plot_audio_segment_filtrado(self):
        # Prueba de la función plot_audio_segment_filtrado
        audio_segment = self.senial  # Usar la señal de prueba
        filtered_segment = self.senial  # Usar la misma señal como ejemplo
        
        self.visualizador.plot_audio_segment_filtrado(audio_segment, filtered_segment, start_time=0)
        # Comprobar si se ha creado el archivo de salida
        output_file = self.output_dir / "test_audio_segment_filtered.png"
        self.assertTrue(output_file.exists(), "El archivo de salida no fue creado.")

    def test_plot_audio_segment_and_spectrogram(self):
        # Prueba de la función plot_audio_segment_and_spectrogram
        audio_segment = self.senial  # Usar la señal de prueba
        
        self.visualizador.plot_audio_segment_and_spectrogram(audio_segment, start_time=0)
        # Comprobar si se ha creado el archivo de salida
        output_file = self.output_dir / "test_audio_spectrogram_segment.png"
        self.assertTrue(output_file.exists(), "El archivo de salida no fue creado.")


if __name__ == '__main__':
    unittest.main()