import unittest
import numpy as np
import sys
import os
# Añade el directorio raíz del proyecto al PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modelo.senial import SenialAudio
from procesador.procesador import Segmenter, HighPassFilter, LowPassFilter



class TestAudioProcessor(unittest.TestCase):
    def setUp(self):
        # Crear una señal de audio de prueba
        self.fs = 44100
        self.data = np.random.rand(self.fs * 2)  # 2 segundos de audio
        self.senial = SenialAudio(self.data, self.fs)

    def test_segmenter(self):
        segmenter = Segmenter(self.senial, 1, 0.5)  # Segmentar desde el segundo 1 por 0.5 segundos
        segmenter.process()
        processed_data = segmenter.get_processed_data()
        self.assertEqual(len(processed_data), int(0.5 * self.fs))

    def test_high_pass_filter(self):
        high_pass = HighPassFilter(self.senial, 1000)
        high_pass.process()
        processed_data = high_pass.get_processed_data()
        # Verificar que las frecuencias bajas se hayan atenuado
        # ... (implementar una prueba más robusta para verificar la atenuación)

    def test_low_pass_filter(self):
        low_pass = LowPassFilter(self.senial, 1000)
        low_pass.process()
        processed_data = low_pass.get_processed_data()
        # Verificar que las frecuencias altas se hayan atenuado
        # ... (implementar una prueba más robusta para verificar la atenuación)

    """ def test_invalid_input(self):
        # Probar con datos de entrada inválidos (e.g., frecuencia de muestreo negativa)
        with self.assertRaises(ValueError):
            Segmenter(self.senial, -1, 0.5)

    def test_processed_data_not_none(self):
        # Verificar que get_processed_data() lance una excepción si no se ha llamado a process()
        processor = AudioProcessor(self.senial)
        with self.assertRaises(Exception):
            processor.get_processed_data() """