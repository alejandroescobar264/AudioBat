__author__ = 'Alejandro Escobar'
__version__ = '1.0.0'
__date__ = '2024/10/22'
__author_email__ = 'alejandroescobar264@gmail.com'

"""
Las responsabilidades se dividen entre diferentes clases separadas en diferentes módulos a implementar.
"""
import os
from pathlib import Path
import modelo.senial
import procesador
import procesador.procesador



class Lanzador:
    """
    Programa Lanzador
    """

    @staticmethod
    def tecla() -> None:
        """
        Función que solicita al usuario presionar cualquier tecla para continuar.

        Esta función espera cualquier entrada del usuario y luego limpia la pantalla.
        """
        input("Presione cualquier tecla para continuar...")
        os.system('clear')

    @staticmethod
    def informar_versiones() -> None:
        """
        Informa las versiones de los componentes
        """
        os.system("clear")
        print("Versiones de los componentes")
        print(f"modelo: {modelo.__version__}")

    @staticmethod
    def ejecutar() -> None:
        """
        Programa principal
        """
        # Se prepara el programa
        Lanzador.informar_versiones()
        Lanzador.tecla()

        os.system("clear")
        print("Inicio - Paso 1 - Carga de la señal")
        # Paso 1 - Se carga la senial
        # Cargar la señal de audio
        
        ruta_archivo = Path("Audio/Grabaciones/AR1/AR1ecAR1303712_20240918_012907.wav")
        senial_audio = modelo.senial.SenialAudioWAV(ruta_archivo)
        
        # Crear carpeta de salida basada en el nombre del archivo de audio
        ruta_salida = Path("Salidas") / ruta_archivo.stem
        os.makedirs(ruta_salida, exist_ok=True)
        
        # Mostrar métricas
        print("    |--> Métricas de la señal")
        senial_audio.metricas()

        # Paso 2 - Se procesa la senial adquirida
        print("Inicio - Paso 2 - Procesamiento")
        
        print("    |--> Se resta la continua")
        DCRemover = procesador.procesador.DCRemover(senial_audio)
        DCRemover.process()
        senial_audio_dc_remove = DCRemover.get_processed_data()

        print("    |--> Se segmenta la señal")
        # Segmentar los primeros 10 segundos
        start_time = 0
        duration = 10
        segmentador = procesador.procesador.Segmenter(senial_audio_dc_remove, start_time, duration)
        segmentador.process()
        segmento_senial = segmentador.get_processed_data()

        print("    |--> Se filtra la señal")
        # Aplicar filtros
        filtro_pasa_altos = procesador.procesador.HighPassFilter(segmento_senial, cutoff_freq=2500)
        filtro_pasa_altos.process()
        segmento_senial_filtrada_altos = filtro_pasa_altos.get_processed_data()

        filtro_pasa_bajos = procesador.procesador.LowPassFilter(segmento_senial_filtrada_altos, cutoff_freq=5000)
        filtro_pasa_bajos.process()
        segmento_senial_filtrada = filtro_pasa_bajos.get_processed_data()
        
        print("    |--> Se calcula la FFT de la señal")
        fft_processor = procesador.procesador.FFTProcessor(segmento_senial_filtrada)
        magitudes, frecuencias = fft_processor.process()
        

        # Paso 3 - Se muestran las seniales
        print("Inicio - Paso 3 - Mostrar Señales")
        
        # Visualizar los resultados
        print("    |--> Guardar señal audio completa")
        senial_audio.graficar(ruta_salida, ruta_archivo.stem)
        print("    |--> Guardar segmento filtrado")
        senial_audio.graficar_segmento_filtrado(segmento_senial, segmento_senial_filtrada, start_time, ruta_salida, ruta_archivo.stem)


if __name__ == "__main__":
    Lanzador().ejecutar()