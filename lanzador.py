__author__ = 'Alejandro Escobar'
__version__ = '1.0.0'
__date__ = '2024/10/22'
__author_email__ = 'alejandroescobar264@gmail.com'

"""
Las responsabilidades se dividen entre diferentes clases separadas en diferentes módulos a implementar.
"""
import os
import modelo


class Lanzador:
    """
    Programa Lanzador
    """

    @staticmethod
    def tecla() -> None:
        """
        Funcion que solicita una tecla para continuar
        """
        while True:
            if input('C para continuar> ') == "C":
                break
        os.system("clear")

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

        # Se instancian las clases que participan del procesamiento
        mi_adquisidor = Configurador.adquisidor
        mi_procesador = Configurador.procesador
        mi_visualizador = Configurador.visualizador
        repositorio_adquisicion = Configurador.rep_adquisicion
        repositorio_procesamiento = Configurador.rep_procesamiento

        os.system("clear")
        print("Inicio - Paso 1 - Adquisicion de la senial")
        # Paso 1 - Se obtiene la senial
        mi_adquisidor.leer_senial()
        senial_adquirida = mi_adquisidor.obtener_senial_adquirida()
        senial_adquirida.fecha_adquisicion = datetime.now().date()
        senial_adquirida.comentario = input('Descripcion de la señal:')
        senial_adquirida.id = int(input('Identificacion (nro entero)'))
        print('Fecha de lectura: {0}'.format(senial_adquirida.fecha_adquisicion))
        print('Cantidad de valores obtenidos {0}'.format(senial_adquirida.cantidad))
        repositorio_adquisicion.auditar(senial_adquirida, "Senial Adquirida")

        Lanzador.tecla()
        print('Se persiste la señal adquirida')
        repositorio_adquisicion.guardar(senial_adquirida)
        print('Señal Guardada')
        repositorio_adquisicion.auditar(senial_adquirida, "Senial Guardada")

        # Paso 2 - Se procesa la senial adquirida
        print("Inicio - Paso 2 - Procesamiento")
        mi_procesador.procesar(senial_adquirida)
        senial_procesada = mi_procesador.obtener_senial_procesada()
        repositorio_procesamiento.auditar(senial_procesada, "Senial Procesada")

        Lanzador.tecla()
        print('Se persiste la señal procesada')
        senial_procesada.comentario = input('Descripción de la señal procesada:')
        senial_procesada.id = int(input('Identificación (nro entero): '))
        repositorio_procesamiento.guardar(senial_procesada)
        print('Señal Procesada Guardada')
        repositorio_procesamiento.auditar(senial_procesada, "Senial Guardada")

        # Paso 3 - Se muestran las seniales
        print("Inicio - Paso 3 - Mostrar Señales")
        adquirida = repositorio_adquisicion.obtener(Configurador.senial_adquirir, senial_adquirida.id)
        print('Señal adquirida----->')
        mi_visualizador.mostrar_datos(adquirida)
        procesada = repositorio_procesamiento.obtener(Configurador.senial_procesar, senial_procesada.id)
        print('Señal procesada----->')
        mi_visualizador.mostrar_datos(procesada)

if __name__ == "__main__":
    Lanzador().ejecutar()