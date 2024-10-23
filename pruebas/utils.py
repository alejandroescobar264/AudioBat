import numpy as np

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