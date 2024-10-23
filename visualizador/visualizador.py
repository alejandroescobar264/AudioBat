"""
Clase que genera la salida y visualizacion del contenido de la señal
"""
from modelo.senial import *
import matplotlib.pyplot as plt


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