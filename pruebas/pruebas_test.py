import unittest
from scipy.io.wavfile import write, read
import numpy as np
import sys
import os

# Añade el directorio raíz del proyecto al PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modelo.senial import SenialAudioWAV, SenialAudio


def generar_senal_senoidal(frecuencia, duracion, frecuencia_muestreo):
    """
    Genera una señal de audio senoidal.

    Args:
        frecuencia (float): Frecuencia de la señal senoidal (Hz).
        duracion (float): Duración de la señal en segundos.
        frecuencia_muestreo (int): Frecuencia de muestreo (Hz).

    Returns:
        np.ndarray: Señal senoidal generada.
    """
    t = np.linspace(0, duracion, int(frecuencia_muestreo * duracion), endpoint=False)
    señal = 0.5 * np.sin(2 * np.pi * frecuencia * t)
    return np.int16(señal * 32767)  # Escalamos a int16 para audio WAV


class TestSenialAudio(unittest.TestCase):

    def setUp(self):
        """
        Método que se ejecuta antes de cada prueba.
        Crea un conjunto de datos simulado (señal senoidal) y una frecuencia de muestreo.
        """
        self.frecuencia_senal = 5  # Frecuencia de la señal senoidal en Hz
        self.duracion_senal = 2  # Duración de la señal en segundos
        self.frecuencia_muestreo = 50  # Frecuencia de muestreo en Hz
        self.datos = generar_senal_senoidal(self.frecuencia_senal, self.duracion_senal, self.frecuencia_muestreo)
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
        self.ruta_archivo = 'test_audio.wav'
        self.frecuencia_senal = 5  # Frecuencia de la señal senoidal en Hz
        self.duracion_senal = 2  # Duración de la señal en segundos
        self.frecuencia_muestreo = 50  # Frecuencia de muestreo en Hz
        self.datos = generar_senal_senoidal(self.frecuencia_senal, self.duracion_senal, self.frecuencia_muestreo)

        # Crear archivo WAV temporal para la prueba
        write(self.ruta_archivo, self.frecuencia_muestreo, self.datos)

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

if __name__ == '__main__':
    unittest.main()
