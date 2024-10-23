import numpy as np
from scipy.io import wavfile

def generar_senial_senoidal(frecuencia, duracion, frecuencia_muestreo):
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

def crear_senial_prueba(ruta_archivo, frecuencia, duracion, frecuencia_muestreo):

    # Generar la señal
    senial_audio = generar_senial_senoidal(frecuencia, duracion, frecuencia_muestreo)

    # Guardar la señal como un archivo WAV
    wavfile.write(ruta_archivo, frecuencia_muestreo, senial_audio)