# Caracterización de Señales de RF - Enlaces Satelitales

Este proyecto es una aplicación desarrollada en Python que permite la caracterización y análisis de señales de radiofrecuencia (RF) provenientes de enlaces satelitales. La herramienta proporciona funcionalidades para:

- **Cargar y procesar archivos CSV** con datos de espectro de frecuencia.
- **Detectar señales y posibles interferencias** en el espectro.
- **Estimar parámetros del canal**, como atenuación y retardo de propagación.
- **Visualizar gráficamente** las señales detectadas y las interferencias.
- **Exportar los resultados** a un archivo Excel para un análisis adicional.

La aplicación cuenta con una interfaz gráfica de usuario (GUI) desarrollada con Tkinter, lo que facilita su uso y permite interactuar con las diferentes funcionalidades de manera intuitiva.

## Índice

- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Funcionalidades](#funcionalidades)
  - [Cargar Archivo CSV](#cargar-archivo-csv)
  - [Procesar Datos](#procesar-datos)
  - [Visualización de Características](#visualización-de-características)
  - [Detección de Interferencias](#detección-de-interferencias)
  - [Estimación de Parámetros de Canal](#estimación-de-parámetros-de-canal)
  - [Exportar a Excel](#exportar-a-excel)
- [Notas Adicionales](#notas-adicionales)
- [Licencia](#licencia)

## Requisitos

Para ejecutar esta aplicación, necesitas tener instalado:

- **Python 3.x**
- Las siguientes librerías de Python:

  - `pandas`
  - `numpy`
  - `matplotlib`
  - `scipy`
  - `pywt`
  - `xlsxwriter`

Estas librerías se pueden instalar fácilmente utilizando `pip`:

```bash
pip install pandas numpy matplotlib scipy pywt xlsxwriter
```

## Instalación

1. **Clona o descarga este repositorio** en tu máquina local.

2. **Navega hasta el directorio del proyecto**:

   ```bash
   cd directorio_del_proyecto
   ```

3. **Ejecuta el script principal**:

   ```bash
   python nombre_del_script.py
   ```

   Asegúrate de reemplazar `nombre_del_script.py` por el nombre real del archivo Python proporcionado.

## Uso

Al ejecutar el script, se abrirá la interfaz gráfica de la aplicación. La interfaz consta de varios elementos que te guiarán a través del proceso de caracterización de señales:

1. **Cargar Archivo CSV**: Haz clic en el botón "Cargar Archivo CSV" para seleccionar el archivo que contiene los datos del espectro de frecuencia.

2. **Ingresar Parámetro de Fecha y Hora**: Introduce el parámetro de fecha y hora correspondiente a la columna que deseas analizar en el archivo CSV.

3. **Procesar Datos**: Haz clic en "Procesar Datos" para iniciar el análisis de las señales presentes en el espectro.

## Funcionalidades

### Cargar Archivo CSV

- La aplicación permite cargar archivos CSV que contienen datos de espectro de frecuencia.
- El archivo CSV debe tener un formato específico, dividido en tres secciones separadas por líneas en blanco.
- La función `leer_csv_especial(ruta_archivo)` se encarga de leer y procesar el archivo, separando las secciones y manejando los datos adecuadamente.

### Procesar Datos

- Una vez cargado el archivo CSV, ingresa el parámetro de fecha y hora correspondiente a la columna que deseas analizar.
- La aplicación normaliza los nombres de las columnas y selecciona los datos relevantes para el análisis.
- Se realiza la detección de picos en el espectro utilizando la función `find_peaks` de `scipy.signal`.
- Se calculan las características de cada señal detectada, como frecuencia central, ancho de banda, amplitud, nivel de ruido y relación señal-ruido (SNR).
- Las señales se asignan a satélites específicos en función de su frecuencia central.

### Visualización de Características

- Después de procesar los datos, se muestra una tabla con las características de las señales detectadas.
- La tabla incluye información detallada de cada señal y permite visualizar los resultados de manera clara.
- Desde esta ventana, puedes acceder a opciones adicionales, como generar gráficas y exportar los datos.

### Detección de Interferencias

- La aplicación puede detectar posibles interferencias en el espectro basándose en el SNR de las señales.
- Señales con un SNR por debajo de un umbral definido (por defecto, 10 dB) se consideran interferencias.
- Se proporciona una gráfica que muestra las interferencias detectadas en el espectro.

### Estimación de Parámetros de Canal

- Se estima la atenuación del canal para cada señal detectada, asumiendo una potencia de transmisión conocida (0 dBm por defecto).
- Se calcula el retardo de propagación del canal, asumiendo una distancia promedio al satélite (600 km para satélites en órbita baja).
- Los resultados se muestran en una nueva ventana con tablas y valores calculados.

### Exportar a Excel

- La aplicación permite exportar la tabla de características de las señales a un archivo Excel.
- Utiliza la librería `xlsxwriter` para crear un archivo Excel con los datos, facilitando su análisis y almacenamiento.

## Notas Adicionales

- **Interfaz Gráfica**: La GUI está desarrollada con Tkinter, la librería estándar de Python para interfaces gráficas. Es simple y fácil de usar.

- **Gráficas**: Las funciones de visualización utilizan Matplotlib para generar gráficas del espectro y las señales detectadas.

- **Procesamiento de Señales**: Se utilizan herramientas de `numpy` y `scipy` para el procesamiento numérico y la detección de picos en el espectro.

- **Compatibilidad**: La aplicación está diseñada para funcionar en sistemas operativos Windows, pero también debería ser compatible con macOS y Linux, siempre que se cumplan los requisitos de Python y las librerías.

## Licencia

Este proyecto se distribuye bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

**Contacto**:

Si tienes preguntas, sugerencias o necesitas asistencia, no dudes en ponerte en contacto con el desarrollador del proyecto.

¡Gracias por utilizar la aplicación de Caracterización de Señales de RF!