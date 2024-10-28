from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
from modelo.senial import SenialAudio

class AudioProcessor(ABC):
    """
    Clase Base Abstracta para procesadores de señal de audio.

    Define una interfaz común para todos los procesadores de señal de audio.
    Las subclases deben implementar los métodos `process` y `get_processed_data`.
    """

    def __init__(self, senial_audio: SenialAudio):
        """
        Inicializa el procesador con la frecuencia de muestreo y los datos de audio.

        Args:
            senial_audio (SenialAudio): Objeto que representa la señal de audio a procesar.
        """
        self.fs: float = senial_audio.frecuencia_muestreo
        self.audio_data: np.ndarray = senial_audio.datos
        self._processed_data: SenialAudio | None = None

    @abstractmethod
    def process(self) -> None:
        """
        Método abstracto que define el procesamiento de la señal de audio.

        Debe implementarse en subclases para realizar el procesamiento específico.
        """
        if self.audio_data.ndim > 1:
            self.audio_data = self.audio_data[:, 0]  # Tomar solo el primer canal si es estéreo

    def get_processed_data(self) -> np.ndarray:
        """
        Devuelve la señal de audio procesada.

        Returns:
            np.ndarray: Datos procesados de la señal de audio.
        """
        if self._processed_data is None:
            raise Exception("La señal aún no ha sido procesada. Llame al método `process` primero.")
        return self._processed_data


class Segmenter(AudioProcessor):
    """
    Clase para extraer un segmento específico de la señal de audio.
    """

    def __init__(self, senial_audio: SenialAudio, start_time: int, duration: int):
        """
        Inicializa el segmentador de señal de audio.

        Args:
            senial_audio (SenialAudio): Objeto que representa la señal de audio a procesar.
            start_time (int): Tiempo de inicio del segmento en segundos.
            duration (int): Duración del segmento en segundos.
        """
        super().__init__(senial_audio)
        self.start_time: int = start_time
        self.duration: int = duration

    def process(self) -> None:
        """
        Extrae el segmento de audio especificado por el tiempo de inicio y la duración.
        """
        start_sample = int(self.start_time * self.fs)
        end_sample = start_sample + int(self.duration * self.fs)
        self._processed_data = self.audio_data[start_sample:end_sample]
        self._processed_data = SenialAudio(self._processed_data, self.fs)  # Convertir a objeto SenialAudio


class HighPassFilter(AudioProcessor):
    """
    Clase para aplicar un filtro pasa-altos a la señal de audio.
    """

    def __init__(self, senial_audio: SenialAudio, cutoff_freq: float, order: int = 5):
        """
        Inicializa el filtro pasa-altos.

        Args:
            senial_audio (SenialAudio): Objeto que representa la señal de audio a procesar.
            cutoff_freq (float): Frecuencia de corte del filtro en Hz.
            order (int, optional): Orden del filtro. Default es 5.
        """
        super().__init__(senial_audio)
        self.cutoff_freq: float = cutoff_freq
        self.order: int = order

    def process(self) -> None:
        """
        Aplica el filtro pasa-altos a la señal de audio.
        """
        nyquist = 0.5 * self.fs
        normal_cutoff = self.cutoff_freq / nyquist
        b, a = butter(self.order, normal_cutoff, btype='high', analog=False)
        self._processed_data = filtfilt(b, a, self.audio_data)
        self._processed_data = SenialAudio(self._processed_data, self.fs)  # Convertir a objeto SenialAudio


class LowPassFilter(AudioProcessor):
    """
    Clase para aplicar un filtro pasa-bajos a la señal de audio.
    """

    def __init__(self, senial_audio: SenialAudio, cutoff_freq: float, order: int = 5):
        """
        Inicializa el filtro pasa-bajos.

        Args:
            senial_audio (SenialAudio): Objeto que representa la señal de audio a procesar.
            cutoff_freq (float): Frecuencia de corte del filtro en Hz.
            order (int, optional): Orden del filtro. Default es 5.
        """
        super().__init__(senial_audio)
        self.cutoff_freq: float = cutoff_freq
        self.order: int = order

    def process(self) -> None:
        """
        Aplica el filtro pasa-bajos a la señal de audio.
        """
        nyquist = 0.5 * self.fs
        normal_cutoff = self.cutoff_freq / nyquist
        b, a = butter(self.order, normal_cutoff, btype='low', analog=False)
        self._processed_data = filtfilt(b, a, self.audio_data)
        self._processed_data = SenialAudio(self._processed_data, self.fs)  # Convertir a objeto SenialAudio


class DCRemover(AudioProcessor):
    """
    Clase para eliminar la componente de continua (DC) de una señal de audio.
    """

    def process(self) -> None:
        """
        Elimina la componente de continua de la señal.
        """
        self._processed_data = self.audio_data - np.mean(self.audio_data)
        self._processed_data = SenialAudio(self._processed_data, self.fs)  # Convertir a objeto SenialAudio


class FFTProcessor(AudioProcessor):
    """
    Clase para aplicar la Transformada Rápida de Fourier (FFT) a una señal de audio.
    """

    def __init__(self, senial_audio: SenialAudio):
        """
        Inicializa el procesador de FFT.

        Args:
            senial_audio (SenialAudio): Objeto que representa la señal de audio a procesar.
        """
        super().__init__(senial_audio)
        self.freqs: np.ndarray | None = None

    def process(self) -> tuple[np.ndarray, np.ndarray, float]:
        """
        Aplica la FFT a la señal de audio y calcula el espectro de frecuencias.

        Returns:
            tuple: Magnitudes de la FFT, frecuencias y frecuencia de muestreo.
        """
        n = len(self.audio_data)
        fft_values = np.fft.fft(self.audio_data)
        fft_freqs = np.fft.fftfreq(n, d=1 / self.fs)

        self._processed_data = np.abs(fft_values[:n // 2])
        self.freqs = fft_freqs[:n // 2]

        return self._processed_data, self.freqs, self.fs


class EventProcessor(AudioProcessor):
    """
    Clase para detectar eventos dentro de la señal de audio.
    """

    def __init__(self, senial_audio: SenialAudio, energy_threshold: float, min_duration: int,
                 focus_freq: tuple[int, int], output_dir: str, filename: str):
        """
        Inicializa el procesador de eventos.

        Args:
            senial_audio (SenialAudio): Objeto que representa la señal de audio a procesar.
            energy_threshold (float): Umbral de energía para detección de eventos.
            min_duration (int): Duración mínima del evento en ms.
            focus_freq (tuple): Rango de frecuencias de enfoque.
            output_dir (str): Directorio de salida.
            filename (str): Nombre del archivo de eventos.
        """
        super().__init__(senial_audio)
        self.energy_threshold: float = energy_threshold
        self.min_duration: int = min_duration
        self.focus_freq: tuple[int, int] = focus_freq
        self._output_dir: str = output_dir
        self._filename: str = os.path.join(self._output_dir, f"{filename}_events.csv")
        self.segment_duration: float = 6 / 1000  # Duración del segmento en segundos
        self.events: list[tuple[float, float]] | None = None

    def process(self) -> None:
        """
        Procesa la señal de audio para detectar eventos y los guarda en un archivo CSV.

        1. Segmenta la señal en trozos de 6 ms.
        2. Calcula la energía de cada segmento.
        3. Detecta eventos basados en la energía y duración.
        4. Guarda los eventos detectados en un archivo CSV.
        """
        segments = self._segmentar_audio()
        self._detectar_eventos(segments)
        self._guardar_csv()

    def _segmentar_audio(self) -> list[np.ndarray]:
        """
        Divide la señal de audio en segmentos de duración fija.

        Returns:
            list: Lista de segmentos de la señal de audio.
        """
        segment_samples = int(self.segment_duration * self.fs)
        return [self.audio_data[i:i + segment_samples] for i in range(0, len(self.audio_data), segment_samples)]

    def _calcular_energia(self, segment: np.ndarray) -> float:
        """
        Calcula la energía de un segmento de audio.

        Args:
            segment (np.ndarray): Segmento de audio.

        Returns:
            float: Energía calculada del segmento.
        """
        return np.sum(segment ** 2)

    def _detectar_eventos(self, segments: list[np.ndarray]) -> None:
        """
        Detecta eventos en la señal basados en la energía y duración.

        Args:
            segments (list): Lista de segmentos de audio.
        """
        self.events = []
        current_event = None
        for i, segment in enumerate(segments):
            energy = self._calcular_energia(segment)
            if energy > self.energy_threshold:
                if current_event is None:
                    current_event = [i]
            else:
                if current_event and i - current_event[0] >= self.min_duration:
                    start_time = current_event[0] * self.segment_duration
                    end_time = i * self.segment_duration
                    self.events.append((start_time, end_time))
                current_event = None

    def _guardar_csv(self) -> None:
        """
        Guarda los eventos detectados en un archivo CSV.
        """
        if not self.events:
            print("No se detectaron eventos.")

        data = [[start, end, (end - start) * 1000] for start, end in self.events]
        df = pd.DataFrame(data, columns=['Inicio', 'Fin', 'Duración (ms)'])
        df.to_csv(self._filename, index=False)


class TimeExpander(AudioProcessor):
    """
    Clase para realizar la expansión temporal de una señal de audio.
    """

    def __init__(self, senial_audio: SenialAudio, expansion_factor: int):
        """
        Inicializa el procesador de expansión temporal.

        Args:
            senial_audio (SenialAudio): Objeto que representa la señal de audio a procesar.
            expansion_factor (int): Factor de expansión temporal.
        """
        super().__init__(senial_audio)
        self.expansion_factor: int = expansion_factor

    def process(self) -> None:
        """
        Realiza la expansión temporal interpolando nuevos puntos entre las muestras originales.
        """
        expanded_length = int(len(self.audio_data) * self.expansion_factor)
        expanded_audio = np.zeros(expanded_length)

        for i in range(expanded_length):
            original_index = int(i / self.expansion_factor)
            expanded_audio[i] = self.audio_data[original_index]

        self._processed_data = SenialAudio(expanded_audio, self.fs)  # Convertir a objeto SenialAudio
