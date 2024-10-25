import unittest
from scipy.io.wavfile import write, read
import sys
import os
from pathlib import Path

# Añade el directorio raíz del proyecto al PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modelo.senial import SenialAudioWAV, SenialAudio
from pruebas.utils import generar_senial_senoidal, crear_senial_prueba


class TestSenialAudio(unittest.TestCase):
    def setUp(self):
        # Generar una señal senoidal para pruebas
        self.frecuencia_senal = 440  # Frecuencia en Hz
        self.duracion_senal = 20  # Duración en segundos
        self.frecuencia_muestreo = 44100  # Frecuencia de muestreo en Hz
        self.datos = generar_senial_senoidal(self.frecuencia_senal, self.duracion_senal, self.frecuencia_muestreo)
        self.senial = SenialAudio(self.datos, self.frecuencia_muestreo)

    def test_obtener_duracion(self):
        duracion_esperada = len(self.datos) / self.frecuencia_muestreo
        self.assertEqual(self.senial.obtener_duracion(), duracion_esperada)


class TestSenialAudioWAV(unittest.TestCase):
    def setUp(self):
        # Crear una señal de prueba en un archivo WAV temporal
        # Generar una señal senoidal para pruebas
        self.frecuencia_senal = 440  # Frecuencia en Hz
        self.duracion_senal = 20  # Duración en segundos
        self.frecuencia_muestreo = 44100  # Frecuencia de muestreo en Hz
        self.ruta_archivo = "test_audio.wav"
        self.ruta_archivo_guardado = "test_audio_guardado.wav"
        crear_senial_prueba(self.ruta_archivo, self.frecuencia_senal, self.duracion_senal, self.frecuencia_muestreo)
        self.senial = SenialAudioWAV(self.ruta_archivo)

    def tearDown(self):
        # Eliminar los archivos de prueba después de cada test
        if os.path.exists(self.ruta_archivo):
            os.remove(self.ruta_archivo)
        if os.path.exists(self.ruta_archivo_guardado):
            os.remove(self.ruta_archivo_guardado)

    def test_duracion(self):
        duracion_esperada = self.duracion_senal  # en segundos
        self.assertAlmostEqual(self.senial.obtener_duracion(), duracion_esperada, places=2)

    def test_metricas(self):
        metricas = self.senial.metricas()
        self.assertIn("duracion", metricas)
        self.assertIn("energia_total", metricas)
        self.assertGreater(metricas["energia_total"], 0)
        self.assertGreater(metricas["valor_rms"], 0)
    
    def test_guardar(self):
        # Guardar la señal en un nuevo archivo
        self.senial.guardar(self.ruta_archivo_guardado)

        # Verificar que el archivo guardado existe
        self.assertTrue(os.path.exists(self.ruta_archivo_guardado), "El archivo guardado no fue creado.")

        # Leer los datos del archivo guardado
        frecuencia_muestreo_guardado, datos_guardados = read(self.ruta_archivo_guardado)

        # Verificar que los datos y la frecuencia de muestreo coincidan
        self.assertEqual(frecuencia_muestreo_guardado, self.senial.frecuencia_muestreo)
        self.assertTrue((datos_guardados == self.senial.datos).all())



if __name__ == '__main__':
    unittest.main()
