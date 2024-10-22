# AudioBat
Librería para procesar registros activos de llamadas de ecolocalización de murciélagos en ambientes con interferencia por ruido ultrasónico de origen antrópico. 

> [!NOTE]
> Este es un TP integrador para Ingeniería de Software II.[^1]

Para instalar los requerimientos emplear el comando:

```
pip install -r requirements.txt
```
Para abordar este trabajo vamos a centrarnos en los requerimientos funcionales clave:

1. **Procesamiento de Archivos de Audio y Preprocesamiento**:
    - El sistema debe permitir la carga y procesamiento de archivos de audio en formato ".wav".
    - El sistema debe realizar preprocesamiento para eliminar ruido ultrasónico de origen abiótico.
    - El sistema debe poder mostrar una gráfica del archivo de audio en el tiempo.
    - El usuario debe poder seleccionar un determinado rango de tiempo en el que realizar los análisis
  
2. **Generación de Espectrogramas y Visualización**:
    - El sistema debe generar espectrogramas a partir de los archivos de audio procesados.
    - El sistema debe permitir guardar los espectrogramas en formatos de imagen estándar (PNG, JPEG).

3. **Identificación Automática de Especies**:
    - El sistema debe identificar automáticamente las especies de murciélagos presentes en los archivos de audio a partir de los patrones acústicos.
    - El sistema debe mostrar métricas clave por especie (frecuencia máxima, mínima, etc.).

4. **Generación de Reportes**:
    - El sistema debe generar reportes automáticos con los resultados del análisis de audio, identificando especies de murciélagos y tipos de llamadas.
    - Los reportes deben estar disponibles en formatos utilizables (PDF, CSV).



[^1]: Facultad de Ingeniería de la Universidad Nacional de Entre Ríos (FIUNER).
