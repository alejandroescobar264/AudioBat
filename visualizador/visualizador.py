"""
Clase que genera la salida y visualizacion del contenido de la señal
"""
from modelo.senial import *
from procesador.procesador import *
import matplotlib.pyplot as plt
import os


class Visualizador:
    
    def __init__(self, output_dir, filename) -> None:
        self.output_dir = output_dir
        self.filename = filename

    def plot_spectrum(self, magnitudes, freqs, fs) -> None:
            """
            Grafica el espectro de frecuencias.

            Args:
                output_dir (Path): Directorio donde guardar la imagen.
                filename (str): Nombre del archivo de salida.
            """
            plt.figure(figsize=(12, 6))
            plt.plot(freqs, magnitudes, color='purple', alpha=0.7)
            plt.title(f'Frequency Spectrum $\\bf{{{self.filename}}}$')
            plt.xlabel('Frequency (Hz)')
            plt.ylabel('Magnitude')
            plt.xlim(0, fs / 2)  # Limitar a la mitad de la frecuencia de muestreo
            plt.grid()
            plt.tight_layout()
            plt.savefig(self.output_dir / f"{self.filename}_frequency_spectrum.png", dpi=300)
            plt.close()
    
    def plot_audio(self, senial_audio: SenialAudio):
    
        audio_times = np.arange(len(senial_audio.datos)) / senial_audio.frecuencia_muestreo
        
        plt.figure(figsize=(12, 8))

        # Subplot para la señal original
        plt.plot(audio_times, senial_audio.datos, color='b', alpha=0.6)
        plt.title(f'Audio Signal $\\bf{{{self.filename}}}$ (Complete)')
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Amplitud')
        plt.grid()
        
        # Ajustar límites del eje x
        plt.xlim([audio_times[0], audio_times[-1]])
                            
        # Guardar la figura en formato PNG
        plt.savefig(self.output_dir / f"{self.filename}_complete_signal.png", dpi=300)
        plt.close()
    
    def plot_audio_segment_filtrado(self, audio_segment, filtered_segment, start_time):
    
        audio_times = np.arange(len(audio_segment)) / audio_segment.frecuencia_muestreo + start_time

        plt.figure(figsize=(12, 8))

        # Subplot para la señal recortada
        plt.subplot(2, 1, 1)
        plt.plot(audio_times, audio_segment.datos, color='b', alpha=0.6)
        plt.title(f'Audio Signal $\\bf{{{self.filename}}}$ (Segment, DC Removed)')
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Amplitud')
        plt.grid()
        
        # Ajustar límites del eje x
        plt.xlim([audio_times[0], audio_times[-1]])

        # Subplot para la señal filtrada
        plt.subplot(2, 1, 2)
        plt.plot(audio_times, filtered_segment.datos, color='g', alpha=0.6)
        plt.title(f'Filtered Audio Signal $\\bf{{{self.filename}}}$ (HighPass + LowPass)')
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Amplitud')
        plt.grid()
        
        # Ajustar límites del eje x
        plt.xlim([audio_times[0], audio_times[-1]])

        plt.tight_layout()

        # Guardar la figura en formato PNG
        plt.savefig(self.output_dir / f"{self.filename}_segment_filtered.png", dpi=300)
        plt.close()
    

    def plot_audio_segment_and_spectrogram(self, audio_segment, start_time, focus_freq=None):
        """
        Grafica un segmento de audio y su espectrograma.

        Args:
            audio_segment (np.ndarray): Segmento de audio.
            sample_rate (int): Frecuencia de muestreo.
            start_time (float): Tiempo de inicio del segmento.
            focus_freq (tuple, optional): Rango de frecuencias a enfocar.
        """
        fs = audio_segment.frecuencia_muestreo
        
        # Graficar la señal filtrada
        audio_times = np.arange(len(audio_segment)) / fs + start_time

        plt.figure(figsize=(12, 8))

        # Subplot para la señal filtrada
        plt.subplot(2, 1, 1)
        plt.plot(audio_times, audio_segment.datos, color='g', alpha=0.6)
        plt.title('Filtered Audio Signal $\\bf{{{self.filename}}}$ (HighPass + LowPass)')
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Amplitud')

        plt.grid(which='major', color='#666666', linestyle='-')
        plt.grid(which='minor', color='#999999', linestyle=':')
        plt.minorticks_on()
        
        # Ajustar límites del eje x
        plt.xlim([audio_times[0], audio_times[-1]])

        # Subplot para el espectrograma
        plt.subplot(2, 1, 2)
        Sxx, freqs, times, im = plt.specgram(audio_segment.datos, Fs=fs, NFFT=1024, noverlap=512, cmap='binary')
        
        if focus_freq is not None:
            freq_mask = np.logical_and(freqs >= focus_freq[0], freqs <= focus_freq[1])
            plt.pcolormesh(times, freqs[freq_mask], 10 * np.log10(Sxx[freq_mask, :]), shading='gouraud', cmap='binary')
            plt.ylim(focus_freq)  # Limitar las frecuencias visibles al rango de enfoque
        else:
            plt.pcolormesh(times, freqs, 10 * np.log10(Sxx), shading='gouraud', cmap='binary')

        plt.title(f'Spectrogram of Filtered Audio Segment $\\bf{{{self.filename}}}$')
        plt.ylabel('Frecuencia (Hz)')
        plt.xlabel('Tiempo (s)')
        plt.colorbar(label='Intensidad (dB)', location='bottom')

        # Ajustar límites del eje x
        plt.xlim([audio_times[0], audio_times[-1]])

        plt.tight_layout()
        
        
        # Guardar figura como PNG
        plt.savefig(self.output_dir / f"{self.filename}_spectrogram_segment.png")
        plt.close()
    
    def plot_spectrogram_events_complete(self, event_processor:EventProcessor):
        """
        Visualiza el espectrograma del segmento y marca los eventos.
        Recorta los eventos y los guarda como archivos de audio.
        """
        
        fs = event_processor.fs
        
        # Calcular el espectrograma
        Sxx, freqs, times, im = plt.specgram(event_processor.audio_data, Fs=fs, NFFT=1024, noverlap=512, cmap='binary')

        
        # Crear figura y ejes
        fig, ax = plt.subplots(figsize=(10, 4))
        
        if event_processor.focus_freq is not None:
            freq_mask = np.logical_and(freqs >= event_processor.focus_freq[0], freqs <= event_processor.focus_freq[1])
            plt.pcolormesh(times, freqs[freq_mask], 10 * np.log10(Sxx[freq_mask, :]), shading='gouraud', cmap='binary')
            plt.ylim(event_processor.focus_freq)  # Limitar las frecuencias visibles al rango de enfoque
        else:
            plt.pcolormesh(times, freqs, 10 * np.log10(Sxx), shading='gouraud', cmap='binary')
        
        
        plt.title(f'Spectrogram With Detected Events of $\\bf{{{self.filename}}}$')
        plt.ylabel('Frecuencia (Hz)')
        plt.xlabel('Tiempo (s)')
        plt.colorbar(label='Intensidad (dB)', location='bottom')

        plt.tight_layout()

        # Agregar marcas para los eventos
        for start_time, end_time in event_processor.events:
            ax.axvline(x=start_time, color='red', linestyle='--')
            ax.axvline(x=end_time, color='red', linestyle='--')

        # Crear carpeta de salida basada en el nombre del archivo de audio
        os.makedirs(self.output_dir/"eventos", exist_ok=True)

        # Guardar la figura
        plt.savefig(self.output_dir /"eventos"/ f"{self.filename}_spectrogram_events.png")
        plt.close()
    
    
    def plot_spectrogram_events_single(self, event_processor:EventProcessor):
        
        fs = event_processor.fs
    
        for i, (start_time, end_time) in enumerate(event_processor.events):
            # Ajustar el inicio y fin del evento para incluir 10 ms antes y después
            buffer_ms = 100  # 10 milisegundos
            adjusted_start_time = max(0, start_time - buffer_ms / 1000)  # Convertir a segundos
            adjusted_end_time = min(len(event_processor.audio_data) / fs, end_time + buffer_ms / 1000)

            start_index = int(adjusted_start_time * fs)
            end_index = int(adjusted_end_time * fs)
            event_audio = event_processor.audio_data[start_index:end_index]

            # Calcular el espectrograma del evento
            Sxx_event, freqs_event, times_event, im_event = plt.specgram(event_audio, Fs=fs, NFFT=1024, noverlap=512, cmap='binary')

            # Crear una nueva figura para el sub-espectrograma
            plt.figure()
            
            if event_processor.focus_freq is not None:
                freq_mask = np.logical_and(freqs_event >= event_processor.focus_freq[0], freqs_event <= event_processor.focus_freq[1])
                plt.pcolormesh(times_event, freqs_event[freq_mask], 10 * np.log10(Sxx_event[freq_mask, :]), shading='gouraud', cmap='binary')
                plt.ylim(event_processor.focus_freq)  # Limitar las frecuencias visibles al rango de enfoque
            else:
                plt.pcolormesh(times_event, freqs_event, 10 * np.log10(Sxx_event), shading='gouraud', cmap='binary')
            
            plt.title(f"Espectrograma del evento {i}")
            plt.ylabel('Frecuencia (Hz)')
            plt.xlabel('Tiempo (s)')
            plt.colorbar(label='Intensidad (dB)', location='bottom')
            plt.tight_layout()
            
            # Crear carpeta de salida basada en el nombre del archivo de audio
            os.makedirs(self.output_dir/"eventos"/"individuales", exist_ok=True)
        
            plt.savefig(self.output_dir/"eventos"/"individuales"/ f"espectograma_evento_{i}.png")
            plt.close()