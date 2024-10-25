import unittest
import numpy as np
import sys
import os
# Añade el directorio raíz del proyecto al PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modelo.senial import SenialAudio
from procesador.procesador import (
    HighPassFilter,
    LowPassFilter,
    DCRemover,
    Segmenter,
    FFTProcessor,
    EventProcessor,
)
from pruebas.utils import generar_senial_senoidal, crear_senial_prueba
from modelo.senial import SenialAudioWAV



class TestProcesadores(unittest.TestCase):
    def setUp(self):
        # Crear una señal senoidal de prueba
        self.frecuencia_muestreo = 44100  # Hz
        self.frecuencia_senal = 440  # Frecuencia de la señal en Hz
        self.duracion_senal = 20  # Duración de la señal en segundos
        self.datos = generar_senial_senoidal(self.frecuencia_senal, self.duracion_senal, self.frecuencia_muestreo)
        self.ruta_archivo = "test_audio.wav"
        crear_senial_prueba(self.ruta_archivo, self.frecuencia_senal, self.duracion_senal, self.frecuencia_muestreo)
        self.senial = SenialAudioWAV(self.ruta_archivo)
    
    def tearDown(self):
        # Eliminar archivos creados durante las pruebas
        if os.path.exists(self.ruta_archivo):
            os.remove(self.ruta_archivo)
        if os.path.exists("test_audio_events.csv"):
            os.remove("test_audio_events.csv")

    def test_filtro_pasa_altos(self):
        filtro = HighPassFilter(self.senial, cutoff_freq=500)
        filtro.process()
        procesado = filtro.get_processed_data()

        # Verificar que la salida no sea None y que tenga la misma longitud que la entrada
        self.assertIsNotNone(procesado)
        self.assertEqual(len(procesado.datos), len(self.datos))

    def test_filtro_pasa_bajos(self):
        filtro = LowPassFilter(self.senial, cutoff_freq=1500)
        filtro.process()
        procesado = filtro.get_processed_data()

        # Verificar que la salida no sea None y que tenga la misma longitud que la entrada
        self.assertIsNotNone(procesado)
        self.assertEqual(len(procesado.datos), len(self.datos))

    def test_dc_remover(self):
        # Agregar un offset a la señal
        offset_data = self.datos + 1000
        senial_offset = SenialAudio(offset_data, self.frecuencia_muestreo)

        # Eliminar la componente de continua
        dc_remover = DCRemover(senial_offset)
        dc_remover.process()
        procesado = dc_remover.get_processed_data()

        # Verificar que el promedio esté cercano a cero
        self.assertAlmostEqual(np.mean(procesado.datos), 0, places=1)

    def test_segmentador(self):
        start_time = 0.5  # Segundo de inicio
        duration = 1  # Duración del segmento en segundos
        segmentador = Segmenter(self.senial, start_time, duration)
        segmentador.process()
        procesado = segmentador.get_processed_data()

        # Verificar que la duración del segmento sea la esperada
        self.assertEqual(len(procesado.datos), int(duration * self.frecuencia_muestreo))

    def test_fft_processor(self):
        fft_processor = FFTProcessor(self.senial)
        magnitudes, frecuencias, frecuencia_muestreo = fft_processor.process()

        # Verificar que el número de frecuencias sea la mitad de la señal original (solo frecuencias positivas)
        self.assertEqual(len(magnitudes), len(self.datos) // 2)
        self.assertEqual(len(frecuencias), len(self.datos) // 2)

    def test_event_processor(self):
        # Procesador de eventos con umbral bajo para capturar la señal
        energy_threshold = 1e+3
        min_duration = 5
        focus_freq = (500, 2000)  # Rango de frecuencia de interés
        output_dir = "."
        event_processor = EventProcessor(self.senial, energy_threshold, min_duration, focus_freq, output_dir, "test_audio")
        event_processor.process()
        
        # Verificar que el archivo guardado existe
        self.assertTrue(os.path.exists("test_audio_events.csv"), "El archivo guardado no fue creado.")

        # Verificar que haya eventos detectados
        self.assertIsNotNone(event_processor.events)

if __name__ == '__main__':
    unittest.main()