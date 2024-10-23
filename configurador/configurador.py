from modelo import senial
#from modelo.procesadores import ProcesadorFFT  # Importar el procesador FFT
import json
from typing import Any

# Ruta del archivo de configuración
ruta = "./configurador/configuracion.json"

# Leer el archivo y convertirlo a diccionario
with open(ruta) as archivo:
    configuracion = json.load(archivo)

def definir_senial_procesar(ruta_archivo: str) -> Any:
    """
    Define el tipo de señal a procesar, basado en la configuración.
    :param ruta_archivo: Ruta del archivo de audio.
    :return: Instancia de la señal a procesar.
    """
    if configuracion['configuracion']['senial_pro']['tipo'] == "WAV":
        return senial.SenialAudioWAV(ruta_archivo)
    else:
        raise ValueError("Tipo de señal no soportado")

def definir_procesador() -> Any:
    """
    Define el procesador a utilizar, basado en la configuración.
    :return: Instancia del procesador a utilizar.
    """
    #if configuracion['configuracion']['procesador']['parametros']['id'] == "FFT":
    #    return ProcesadorFFT()
    #else:
    #    raise ValueError("Procesador no soportado")
    pass

def definir_visualizador() -> Any:
    """
    Define el visualizador a utilizar.
    :return: Instancia del visualizador.
    """
    # Aquí puedes definir el visualizador según sea necesario
    pass

class Configurador:
    """
    El Configurador es un contenedor de objetos que participan en la solución.
    """
    senial_procesar = definir_senial_procesar(configuracion['configuracion']['directorio_datos'])

    # Configura el procesador según el archivo de configuración
    #procesador = definir_procesador()

    # Si es necesario, puedes agregar aquí la configuración del visualizador
    # visualizador = definir_visualizador()

