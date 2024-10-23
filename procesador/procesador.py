from abc import ABC, abstractmethod
import numpy as np
from scipy.signal import butter, filtfilt
from modelo.senial import SenialAudio

class AudioProcessor(ABC):
    """
    Clase Base Abstracta para procesadores de señal de audio.

    Esta clase define una interfaz común para todos los procesadores de señal de audio.
    Las subclases deben heredar de esta clase e implementar los métodos abstractos
    `process` y `get_processed_data` para realizar el procesamiento específico y
    devolver la señal procesada.
    """

    def __init__(self, senial_audio: SenialAudio):
        """
        Inicializa el procesador con la frecuencia de muestreo (fs) y los datos de audio.

        Args:
            fs (float): Frecuencia de muestreo del audio.
            audio_data (np.ndarray): Arreglo de NumPy con los datos del audio.
        """
        self.fs = senial_audio.frecuencia_muestreo
        self.audio_data = senial_audio.datos
        self._processed_data = None

    @abstractmethod
    def process(self) -> None:
        """
        Método abstracto que define el procesamiento de la señal de audio.

        Este método debe implementarse en las subclases para realizar el procesamiento
        específico de cada tipo de procesador.
        """
        # Asegurarse de que el audio sea mono
        if self.audio_data.ndim > 1:
            self.audio_data = self.audio_data[:, 0]  # Tomar solo el primer canal si es estéreo
            

    def get_processed_data(self) -> np.ndarray:
        """
        Devuelve la señal de audio procesada.

        Returns:
            np.ndarray: Arreglo de NumPy con los datos del audio procesado.
        """
        if self._processed_data is None:
            raise Exception("La señal aún no ha sido procesada. Llame al método `process` primero.")
        return self._processed_data


class Segmenter(AudioProcessor):
    """
    Clase Segmenter para extraer un segmento específico de la señal de audio.
    """

    def __init__(self, senial_audio: SenialAudio, start_time: int, duration: int):
        """
        Inicializa el procesador Segmentador.

        Args:
            fs (float): Frecuencia de muestreo del audio.
            audio_data (np.ndarray): Arreglo de NumPy con los datos del audio.
            start_time (float): Tiempo de inicio del segmento en segundos.
            duration (float): Duración del segmento en segundos.
        """
        super().__init__(senial_audio)
        self.start_time = start_time
        self.duration = duration

    def process(self) -> None:
        """
        Extrae el segmento de audio especificado.
        """
        start_sample = int(self.start_time * self.fs)
        end_sample = start_sample + int(self.duration * self.fs)
        self._processed_data = self.audio_data[start_sample:end_sample]
        
        # Crear un nuevo objeto SenialAudio con los datos procesados
        processed_signal = SenialAudio(self._processed_data, self.fs)
        self._processed_data = processed_signal

class HighPassFilter(AudioProcessor):
    """
    Clase HighPassFilter para aplicar un filtro pasa altos a la señal de audio.
    """

    def __init__(self, senial_audio: SenialAudio, cutoff_freq, order=5):
        """
        Inicializa el procesador HighPassFilter.

        Args:
            fs (float): Frecuencia de muestreo del audio.
            audio_data (np.ndarray): Arreglo de NumPy con los datos del audio.
            cutoff (float): Frecuencia de corte del filtro en Hz.
            order (int, optional): Orden del filtro. Defaults to 5.
        """
        super().__init__(senial_audio)
        self.cutoff_freq = cutoff_freq
        self.order = order

    def process(self) -> None:
        """
        Aplica el filtro pasa altos a la señal de audio.
        """
        nyquist = 0.5 * self.fs
        normal_cutoff = self.cutoff_freq / nyquist
        b, a = butter(self.order, normal_cutoff, btype='high', analog=False)
        self._processed_data = filtfilt(b, a, self.audio_data)
        
        # Crear un nuevo objeto SenialAudio con los datos procesados
        processed_signal = SenialAudio(self._processed_data, self.fs)
        self._processed_data = processed_signal

class LowPassFilter(AudioProcessor):
    """
    Clase LowPassFilter para aplicar un filtro pasa bajos a la señal de audio.
    """

    def __init__(self, senial_audio: SenialAudio, cutoff_freq, order=5):
        """
        Inicializa el procesador LowPassFilter.

        Args:
            fs (float): Frecuencia de muestreo del audio.
            audio_data (np.ndarray): Arreglo de NumPy con los datos del audio.
            cutoff (float): Frecuencia de corte del filtro en Hz.
            order (int, optional): Orden del filtro. Defaults to 5.
        """
        super().__init__(senial_audio)
        self.cutoff_freq = cutoff_freq
        self.order = order

    def process(self) -> None:
        """
        Aplica el filtro pasa bajos a la señal de audio.
        """
        nyquist = 0.5 * self.fs
        normal_cutoff = self.cutoff_freq / nyquist
        b, a = butter(self.order, normal_cutoff, btype='low', analog=False)
        self._processed_data = filtfilt(b, a, self.audio_data)
        
        # Crear un nuevo objeto SenialAudio con los datos procesados
        processed_signal = SenialAudio(self._processed_data, self.fs)
        self._processed_data = processed_signal


class DCRemover(AudioProcessor):
    """
    Clase DCRemover para eliminar la componente de continua de una señal de audio.
    """

    def process(self) -> None:
        """
        Elimina la componente de continua de la señal.
        """
        self._processed_data = (self.audio_data - np.mean(self.audio_data) )
        
        # Crear un nuevo objeto SenialAudio con los datos procesados
        processed_signal = SenialAudio(self._processed_data, self.fs)
        self._processed_data = processed_signal


class FFTProcessor(AudioProcessor):
    """
    Clase para aplicar la Transformada Rápida de Fourier (FFT) a una señal de audio.
    """
    def __init__(self, senial_audio: SenialAudio):
        """
        Inicializa el procesador FFTProcessor.
        
        """
        super().__init__(senial_audio)
        self.freqs = None
        
    def process(self) -> None:
        """
        Aplica la FFT a la señal de audio y calcula el espectro de frecuencias.
        """
        # Aplicar la FFT
        n = len(self.audio_data)
        fft_values = np.fft.fft(self.audio_data)
        fft_freqs = np.fft.fftfreq(n, d=1/self.fs)

        # Obtener magnitudes y limitar a frecuencias positivas
        self._processed_data = np.abs(fft_values[:n//2])
        self.freqs = fft_freqs[:n//2]
        
        return self._processed_data, self.freqs, self.fs
    