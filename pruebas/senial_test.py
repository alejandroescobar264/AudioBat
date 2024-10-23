import unittest
from scipy.io.wavfile import write, read
import sys
import os
from pathlib import Path

# Añade el directorio raíz del proyecto al PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modelo.senial import SenialAudioWAV, SenialAudio
from pruebas.utils import *



class TestSenialAudio(unittest.TestCase):

    def setUp(self):
        """
        Método que se ejecuta antes de cada prueba.
        Crea un conjunto de datos simulado (señal senoidal) y una frecuencia de muestreo.
        """
        self.frecuencia_senal = 5  # Frecuencia de la señal senoidal en Hz
        self.duracion_senal = 2  # Duración de la señal en segundos
        self.frecuencia_muestreo = 50  # Frecuencia de muestreo en Hz
        self.datos = generar_senial_senoidal(self.frecuencia_senal, self.duracion_senal, self.frecuencia_muestreo)
        self.senial = SenialAudio(self.datos, self.frecuencia_muestreo)

    def test_obtener_duracion(self):
        """
        Verifica que la duración de la señal de audio sea correcta.
        """
        duracion_esperada = len(self.datos) / self.frecuencia_muestreo
        self.assertEqual(self.senial.obtener_duracion(), duracion_esperada)

class TestSenialAudioWAV(unittest.TestCase):

    def setUp(self):
        """
        Método que se ejecuta antes de cada prueba.
        Crea un archivo WAV temporal con una señal senoidal.
        """
        self.ruta_archivo = Path("pruebas/test_audio.wav")
        self.frecuencia_senal = 5  # Frecuencia de la señal senoidal en Hz
        self.duracion_senal = 2  # Duración de la señal en segundos
        self.frecuencia_muestreo = 50  # Frecuencia de muestreo en Hz
        self.datos = generar_senial_senoidal(self.frecuencia_senal, self.duracion_senal, self.frecuencia_muestreo)
        crear_senial_prueba(self.ruta_archivo, self.frecuencia_senal, self.duracion_senal, self.frecuencia_muestreo)
        self.senial = SenialAudioWAV(self.ruta_archivo)

    def tearDown(self):
        """
        Método que se ejecuta después de cada prueba.
        Elimina el archivo WAV temporal.
        """
        if os.path.exists(self.ruta_archivo):
            os.remove(self.ruta_archivo)

    def test_cargar_wav(self):
        """
        Verifica que los datos de la señal WAV se carguen correctamente.
        """
        senial_wav = SenialAudioWAV(self.ruta_archivo)
        self.assertTrue(np.array_equal(senial_wav.datos, self.datos))
        self.assertEqual(senial_wav.frecuencia_muestreo, self.frecuencia_muestreo)

    def test_guardar_wav(self):
        """
        Verifica que los datos de la señal se guarden correctamente en un archivo WAV.
        """
        senial_wav = SenialAudioWAV(self.ruta_archivo)
        nueva_ruta_archivo = 'test_audio_guardado.wav'

        # Guardar la señal en un nuevo archivo
        senial_wav.guardar(nueva_ruta_archivo)

        # Leer el archivo guardado y verificar los datos
        frecuencia_muestreo_guardado, datos_guardados = read(nueva_ruta_archivo)

        self.assertTrue(np.array_equal(datos_guardados, self.datos))
        self.assertEqual(frecuencia_muestreo_guardado, self.frecuencia_muestreo)

        # Eliminar archivo temporal
        if os.path.exists(nueva_ruta_archivo):
            os.remove(nueva_ruta_archivo)
    
    def test_graficar_segmento_filtrado(self):
        
        # Graficar el segmento y la señal filtrada
        self.senial.graficar_segmento_filtrado(self.senial, self.senial, 0, Path("pruebas"), self.ruta_archivo.stem)

        # Verificar que el archivo de imagen se haya creado
        self.assertTrue(os.path.exists("pruebas/test_audio_segment_filtered.png"))
        
        # Eliminar archivo temporal
        if os.path.exists("pruebas/test_audio_segment_filtered.png"):
            os.remove("pruebas/test_audio_segment_filtered.png")

    def test_excepcion_ruta_invalida(self):
        with self.assertRaises(FileNotFoundError):
            SenialAudioWAV("ruta/invalida.wav")

if __name__ == '__main__':
    unittest.main()
