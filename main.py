import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.fft import fft
from scipy.signal import resample

def load_wav(file_path):
    # Cargar archivo WAV
    sample_rate, data = wavfile.read(file_path)
    return sample_rate, data

def plot_spectrogram(data, sample_rate, title):
    # Graficar el sonograma
    plt.figure(figsize=(10, 6))
    plt.specgram(data, Fs=sample_rate, NFFT=1024, noverlap=512, cmap='plasma')
    plt.title(title)
    plt.ylabel('Frecuencia (Hz)')
    plt.xlabel('Tiempo (s)')
    plt.colorbar(label='Intensidad (dB)')
    plt.show()

def fft_analysis(data, sample_rate):
    # Transformada de Fourier
    N = len(data)
    T = 1.0 / sample_rate
    yf = fft(data)
    xf = np.fft.fftfreq(N, T)[:N//2]
    return xf, np.abs(yf[:N//2])

def main(file_path):
    # Cargar archivo WAV
    sample_rate, data = load_wav(file_path)
           
    # Mostrar el sonograma del archivo original
    plot_spectrogram(data, sample_rate, f"Sonograma de {file_path}")
        
    # Realizar análisis frecuencial (Transformada de Fourier)
    xf, yf = fft_analysis(data, sample_rate)
    plt.plot(xf, yf)
    plt.title('Análisis de frecuencia')
    plt.xlabel('Frecuencia (Hz)')
    plt.ylabel('Amplitud')
    plt.grid()
    plt.show()

if __name__ == "__main__":
    file_path = "Audio/Grabaciones/AR3/M_molossus.wav"  # Cambia este archivo por tu archivo WAV
    main(file_path)
