import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
from scipy.signal import find_peaks
import re
import warnings
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk  # Para usar Treeview y mejorar la estética de la tabla
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')  # Usar TkAgg como backend de Matplotlib
import pywt  # Para la Transformada Wavelet
import xlsxwriter  # Para exportar a Excel

warnings.filterwarnings("ignore")

# Funciones para el procesamiento de datos
def leer_csv_especial(ruta_archivo):
    """
    Función para cargar archivo CSV
    """
    with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
        contenido = archivo.read()

    # Dividir el contenido en las tres secciones
    secciones = contenido.split('\n\n')

    # Función para reemplazar comas por puntos en valores numéricos
    def reemplazar_comas(valor):
        try:
            return valor.replace(',', '.')
        except AttributeError:
            return valor

    # Procesar la primera sección
    df1 = pd.read_csv(io.StringIO(secciones[0]), sep=';', header=None)

    # Procesar la segunda sección
    df2 = pd.read_csv(io.StringIO(secciones[1]), sep=';')
    df2 = df2.applymap(reemplazar_comas)
    for columna in df2.columns:
        df2[columna] = pd.to_numeric(df2[columna], errors='ignore')

    # Procesar la tercera sección
    df3 = pd.read_csv(io.StringIO(secciones[2]), sep=';')
    df3 = df3.applymap(reemplazar_comas)
    for columna in df3.columns:
        df3[columna] = pd.to_numeric(df3[columna], errors='ignore')

    return df1, df2, df3

def normalizar_columna(columna):
    # Eliminar espacios adicionales y convertir a minúsculas
    columna = columna.strip().lower()
    # Reemplazar múltiples espacios por uno solo
    columna = re.sub(r'\s+', ' ', columna)
    return columna

def dBm_to_mW(dBm):
    return 10 ** (dBm / 10)

# Funciones de procesamiento y análisis
def detectar_interferencias():
    """
    Detecta y clasifica posibles interferencias en la señal.
    """
    global interferencias
    interferencias = []

    # Umbral para detección de interferencias (por ejemplo, señales con SNR < 10 dB)
    umbral_snr = 10

    # Utilizar los picos ya detectados
    for idx, señal in df_caracteristicas.iterrows():
        SNR = señal['Relación señal-ruido (SNR) [dB]']
        if SNR < umbral_snr:
            interferencia = {
                'Señal': señal['Señal'],
                'Tipo': 'Interferencia',
                'Frecuencia central [Hz]': señal['Frecuencia central [Hz]'],
                'SNR [dB]': SNR
            }
            interferencias.append(interferencia)

    if interferencias:
        plot_interferencias()
    else:
        messagebox.showinfo("Resultado", "No se detectaron interferencias significativas.")

def plot_interferencias():
    """
    Grafica las interferencias detectadas en la señal.
    """
    plt.figure(figsize=(12, 6))
    plt.plot(frec_mag['Frequency [Hz]'], frec_mag['Magnitude [dBm]'], label='Espectro de frecuencia')

    # Marcar las interferencias
    for interferencia in interferencias:
        frec_central = interferencia['Frecuencia central [Hz]']
        plt.axvline(frec_central, color='r', linestyle='--', label=f"Interferencia en {frec_central/1e6:.2f} MHz")

    plt.xlabel('Frecuencia [Hz]')
    plt.ylabel('Magnitud [dBm]')
    plt.title('Interferencias detectadas en el espectro')
    plt.legend()
    plt.grid(True)
    plt.show()

def estimar_atenuacion():
    """
    Estima la atenuación del canal para cada señal detectada.
    """
    global df_atenuacion
    # Supongamos una potencia de transmisión conocida (por ejemplo, 0 dBm)
    potencia_transmitida = 0  # dBm

    atenuaciones = []
    for idx, señal in df_caracteristicas.iterrows():
        potencia_recibida = señal['Amplitud/ Potencia [dBm]']
        atenuacion = potencia_transmitida - potencia_recibida
        atenuaciones.append({
            'Señal': señal['Señal'],
            'Frecuencia central [Hz]': señal['Frecuencia central [Hz]'],
            'Atenuación [dB]': atenuacion
        })

    df_atenuacion = pd.DataFrame(atenuaciones)
    mostrar_parametros_canal()

def estimar_retardo():
    """
    Estima el retardo de propagación del canal.
    """
    # Supongamos una distancia promedio al satélite (por ejemplo, 600 km para satélites en órbita baja)
    distancia = 600e3  # metros

    # Velocidad de la luz
    c = 3e8  # m/s

    retardo = distancia / c  # segundos
    return retardo

def asignar_satellite():
    """
    Asigna cada señal detectada a un satélite basado en su frecuencia central.
    """
    # Rangos de frecuencia de los satélites en Hz
    rango_misc = (400e6, 450e6)
    rango_facsat = (430e6, 440e6)

    satelites = []
    for idx, señal in df_caracteristicas.iterrows():
        frec_central = señal['Frecuencia central [Hz]']
        if rango_misc[0] <= frec_central <= rango_misc[1]:
            if rango_facsat[0] <= frec_central <= rango_facsat[1]:
                satelite = 'EM MISC & EM FACSAT'
            else:
                satelite = 'EM MISC'
        elif rango_facsat[0] <= frec_central <= rango_facsat[1]:
            satelite = 'EM FACSAT'
        else:
            satelite = 'Desconocido'
        satelites.append(satelite)

    df_caracteristicas['Satélite'] = satelites

def exportar_a_excel():
    """
    Exporta la tabla de características a un archivo Excel.
    """
    # Obtener la ruta y nombre del archivo a guardar
    archivo_excel = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx")],
        title="Guardar tabla de características como Excel"
    )
    if not archivo_excel:
        return  # El usuario canceló la operación

    try:
        df_caracteristicas.to_excel(archivo_excel, index=False)
        messagebox.showinfo("Exportar Excel", f"Tabla exportada a Excel:\n{archivo_excel}")
    except Exception as e:
        messagebox.showerror("Error", f"Error al exportar a Excel: {e}")

# Funciones para la interfaz gráfica
def load_csv():
    global df1, df2, df3, ruta_archivo
    ruta_archivo = filedialog.askopenfilename(title="Seleccionar archivo CSV", filetypes=[("CSV files", "*.csv")])
    if ruta_archivo:
        try:
            df1, df2, df3 = leer_csv_especial(ruta_archivo)
            messagebox.showinfo("Éxito", "Archivo CSV cargado con éxito")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar el archivo: {e}")

def procesar_datos():
    global frec_mag, df_caracteristicas
    if 'df3' not in globals():
        messagebox.showwarning("Advertencia", "Primero debes cargar un archivo CSV.")
        return

    # Obtener el parámetro de hora ingresado por el usuario
    hora_parametro = hora_entry.get()
    if not hora_parametro:
        messagebox.showwarning("Advertencia", "Por favor, ingresa el parámetro de fecha y hora.")
        return

    # Normalizar el parámetro de hora
    hora_parametro_normalizada = normalizar_columna(hora_parametro)

    # Aplicar la función de normalización a los nombres de las columnas
    df3.columns = [normalizar_columna(col) for col in df3.columns]

    # Buscar la columna que coincida con la hora normalizada
    if hora_parametro_normalizada in df3.columns:
        columnas_seleccionadas = [df3.columns[0], hora_parametro_normalizada]
        frec_mag = df3[columnas_seleccionadas]
    else:
        messagebox.showerror("Error", f"La hora '{hora_parametro}' no coincide con ningún nombre de columna después de normalizar.")
        return

    # Renombrar las columnas con los valores de la fila con índice 1
    frec_mag.columns = frec_mag.iloc[1]

    # Eliminar las dos primeras filas y reiniciar el índice
    frec_mag = frec_mag.iloc[2:].reset_index(drop=True)

    # Asegurando formato de columnas Frecuencia y Magnitud
    frec_mag['Frequency [Hz]'] = frec_mag['Frequency [Hz]'].astype(float)
    frec_mag['Magnitude [dBm]'] = frec_mag['Magnitude [dBm]'].astype(float)

    # Procesar los datos (aplicar filtrado, detección de picos, etc.)
    # Calcular el percentil 20 de las magnitudes
    magnitudes = frec_mag['Magnitude [dBm]'].values
    frecuencias = frec_mag['Frequency [Hz]'].values

    percentile_20 = np.percentile(magnitudes, 20)

    # Seleccionar las magnitudes por debajo del percentil 20
    noise_magnitudes = magnitudes[magnitudes <= percentile_20]

    # Estimar el nivel de ruido como la mediana de estas magnitudes
    noise_level = np.median(noise_magnitudes)

    # Establecer una altura mínima para los picos (por ejemplo, 6 dB por encima del nivel de ruido)
    min_peak_height = noise_level + 60  # Puedes ajustar este valor según sea necesario

    # Encontrar los índices de los picos
    indices_picos, properties = find_peaks(magnitudes, height=min_peak_height)

    # Obtener las frecuencias y magnitudes de los picos
    frecuencias_picos = frecuencias[indices_picos]
    magnitudes_picos = magnitudes[indices_picos]

    # Lista para almacenar las características de cada señal
    caracteristicas = []

    for i, indice_pico in enumerate(indices_picos):
        frec_peak = frecuencias_picos[i]
        mag_peak = magnitudes_picos[i]
        threshold = mag_peak - 3  # Umbral de -3 dB desde el pico

        # Buscar la frecuencia menor (izquierda del pico)
        idx_left = indice_pico
        while idx_left > 0 and magnitudes[idx_left] > threshold:
            idx_left -= 1
        frec_lower = frecuencias[idx_left]

        # Buscar la frecuencia mayor (derecha del pico)
        idx_right = indice_pico
        while idx_right < len(magnitudes) - 1 and magnitudes[idx_right] > threshold:
            idx_right += 1
        frec_upper = frecuencias[idx_right]

        # Calcular la frecuencia central y el ancho de banda
        frec_central = (frec_upper + frec_lower) / 2
        bandwidth = frec_upper - frec_lower

        # Calcular la relación señal-ruido (SNR)
        SNR = mag_peak - noise_level

        # Calcular la potencia de canal
        # Obtener los índices dentro del ancho de banda
        idx_bandwidth = np.where((frecuencias >= frec_lower) & (frecuencias <= frec_upper))[0]

        # Obtener las magnitudes en dBm dentro del ancho de banda
        mags_in_band = magnitudes[idx_bandwidth]

        # Convertir magnitudes de dBm a mW
        powers_mW = dBm_to_mW(mags_in_band)

        # Calcular la potencia total en mW y convertir a dBm
        total_power_mW = np.sum(powers_mW)
        total_power_dBm = 10 * np.log10(total_power_mW)

        # Almacenar las características en un diccionario
        caracteristicas.append({
            'Señal': i + 1,
            'Frecuencia menor [Hz]': frec_lower,
            'Frecuencia mayor [Hz]': frec_upper,
            'Frecuencia central [Hz]': frec_central,
            'Ancho de banda (BW) [Hz]': bandwidth,
            'Amplitud/ Potencia [dBm]': mag_peak,
            'Nivel de ruido [dBm]': noise_level,
            'Relación señal-ruido (SNR) [dB]': SNR,
            'Potencia de canal [dBm]': total_power_dBm
        })

    df_caracteristicas = pd.DataFrame(caracteristicas)

    # Asignar satélites a las señales
    asignar_satellite()

    messagebox.showinfo("Éxito", "Procesamiento de datos completado.")
    # Mostrar tabla de características
    mostrar_caracteristicas()

def mostrar_caracteristicas():
    # Crear una nueva ventana para mostrar la tabla
    ventana = tk.Toplevel(root)
    ventana.title("Características de las señales")
    ventana.geometry("900x500")

    # Crear Treeview para mostrar el DataFrame
    columns = list(df_caracteristicas.columns)
    tree = ttk.Treeview(ventana, columns=columns, show='headings', height=15)
    tree.pack(pady=20, padx=20, fill='both', expand=True)

    # Definir las columnas
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor='center', width=120)

    # Insertar los datos
    for index, row in df_caracteristicas.iterrows():
        tree.insert("", "end", values=list(row))

    # Añadir botones para funcionalidades adicionales
    btn_frame = tk.Frame(ventana)
    btn_frame.pack(pady=10)

    global_btn = tk.Button(btn_frame, text="Gráfica Global", command=plot_global)
    global_btn.pack(side='left', padx=10)

    local_btn = tk.Button(btn_frame, text="Gráfica Local", command=plot_local)
    local_btn.pack(side='left', padx=10)

    interferencia_btn = tk.Button(btn_frame, text="Detectar Interferencias", command=detectar_interferencias)
    interferencia_btn.pack(side='left', padx=10)

    param_canal_btn = tk.Button(btn_frame, text="Estimación Parámetros de Canal", command=estimar_atenuacion)
    param_canal_btn.pack(side='left', padx=10)

    export_excel_btn = tk.Button(btn_frame, text="Exportar a Excel", command=exportar_a_excel)
    export_excel_btn.pack(side='left', padx=10)

def mostrar_parametros_canal():
    # Mostrar resultados en una nueva ventana
    ventana = tk.Toplevel(root)
    ventana.title("Parámetros de Canal Estimados")
    ventana.geometry("600x400")

    # Mostrar atenuaciones
    label_atenuacion = tk.Label(ventana, text="Estimación de Atenuación", font=("Helvetica", 14, "bold"))
    label_atenuacion.pack(pady=10)

    # Crear Treeview para mostrar el DataFrame de atenuaciones
    columns = list(df_atenuacion.columns)
    tree = ttk.Treeview(ventana, columns=columns, show='headings', height=5)
    tree.pack(pady=10, padx=20, fill='both', expand=True)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor='center', width=150)

    for index, row in df_atenuacion.iterrows():
        tree.insert("", "end", values=list(row))

    # Mostrar retardo
    retardo = estimar_retardo()
    label_retardo = tk.Label(ventana, text=f"Retardo de propagación estimado: {retardo*1e3:.2f} ms", font=("Helvetica", 12))
    label_retardo.pack(pady=10)

def plot_detected_signals_global():
    plt.figure(figsize=(12, 6))

    # Graficar el espectro completo en gris claro para referencia
    plt.plot(frec_mag['Frequency [Hz]'], frec_mag['Magnitude [dBm]'], color='lightgray', label='Espectro completo')

    # Colores para diferenciar cada señal
    colores = ['b', 'g', 'r', 'c', 'm', 'y', 'k']

    # Iterar sobre cada señal detectada
    for idx, señal in df_caracteristicas.iterrows():
        frec_lower = señal['Frecuencia menor [Hz]']
        frec_upper = señal['Frecuencia mayor [Hz]']
        señal_num = señal['Señal']

        # Extraer los datos dentro del rango de frecuencia de la señal
        mask = (frec_mag['Frequency [Hz]'] >= frec_lower) & (frec_mag['Frequency [Hz]'] <= frec_upper)
        freqs_signal = frec_mag['Frequency [Hz]'][mask]
        mags_signal = frec_mag['Magnitude [dBm]'][mask]

        # Seleccionar un color para la señal
        color = colores[idx % len(colores)]

        # Graficar la señal
        plt.plot(freqs_signal, mags_signal, color=color, label=f'Señal {señal_num} ({señal["Satélite"]})')

        # Marcar el pico de la señal
        frec_peak = señal['Frecuencia central [Hz]']
        mag_peak = señal['Amplitud/ Potencia [dBm]']
        plt.plot(frec_peak, mag_peak, 'o', color=color)

    plt.xlabel('Frecuencia [Hz]')
    plt.ylabel('Magnitud [dBm]')
    plt.title('Formas de las señales detectadas')
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_detected_signals_local():
    plt.figure(figsize=(12, 6))

    # Colores para diferenciar cada señal
    colores = ['b', 'g', 'r', 'c', 'm', 'y', 'k']

    # Variables para definir el rango total de frecuencias a mostrar
    frec_min_total = None
    frec_max_total = None

    # Iterar sobre cada señal detectada
    for idx, señal in df_caracteristicas.iterrows():
        frec_lower = señal['Frecuencia menor [Hz]']
        frec_upper = señal['Frecuencia mayor [Hz]']
        señal_num = señal['Señal']

        # Expandir el rango de frecuencias para obtener una mayor porción del pico
        bandwidth = frec_upper - frec_lower
        delta_freq = 0.5 * bandwidth  # Puedes ajustar este factor según tus necesidades

        frec_lower_expanded = frec_lower - delta_freq
        frec_upper_expanded = frec_upper + delta_freq

        # Asegurarse de que las frecuencias no salgan del rango de datos
        frec_lower_expanded = max(frec_lower_expanded, frec_mag['Frequency [Hz]'].min())
        frec_upper_expanded = min(frec_upper_expanded, frec_mag['Frequency [Hz]'].max())

        # Actualizar el rango total de frecuencias a mostrar
        if frec_min_total is None or frec_lower_expanded < frec_min_total:
            frec_min_total = frec_lower_expanded
        if frec_max_total is None or frec_upper_expanded > frec_max_total:
            frec_max_total = frec_upper_expanded

        # Extraer los datos dentro del rango de frecuencia expandido
        mask = (frec_mag['Frequency [Hz]'] >= frec_lower_expanded) & (frec_mag['Frequency [Hz]'] <= frec_upper_expanded)
        freqs_signal = frec_mag['Frequency [Hz]'][mask]
        mags_signal = frec_mag['Magnitude [dBm]'][mask]

        # Seleccionar un color para la señal
        color = colores[idx % len(colores)]

        # Graficar la señal
        plt.plot(freqs_signal, mags_signal, color=color, label=f'Señal {señal_num} ({señal["Satélite"]})')

        # Marcar el pico de la señal
        frec_peak = señal['Frecuencia central [Hz]']
        mag_peak = señal['Amplitud/ Potencia [dBm]']
        plt.plot(frec_peak, mag_peak, 'o', color=color)

    # Configurar los límites de los ejes para mostrar solo el rango de frecuencias de interés
    plt.xlim(frec_min_total, frec_max_total)

    plt.xlabel('Frecuencia [Hz]')
    plt.ylabel('Magnitud [dBm]')
    plt.title('Formas de las señales detectadas (Vista Local)')
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_global():
    plot_detected_signals_global()

def plot_local():
    plot_detected_signals_local()

# Función principal para crear la interfaz gráfica
def crear_interfaz():
    global root, hora_entry

    # Creación de la ventana principal
    root = tk.Tk()
    root.title("Caracterización de Señales de RF - Enlaces Satelitales")
    root.geometry("800x600")
    root.config(bg='#34495E')

    # Estilo del título
    title_label = tk.Label(root, text="Caracterización de Señales de RF\nEnlaces Satelitales",
                           font=("Helvetica", 16, "bold"), bg="#34495E", fg="white")
    title_label.pack(pady=10)

    # Botón para cargar CSV
    load_button = tk.Button(root, text="Cargar Archivo CSV", font=("Helvetica", 12), command=load_csv,
                            bg="#1ABC9C", fg="white", padx=10, pady=5)
    load_button.pack(pady=10)

    # Entrada para el parámetro de hora
    hora_frame = tk.Frame(root, bg="#34495E")
    hora_frame.pack(pady=10)

    hora_label = tk.Label(hora_frame, text="Ingrese el parámetro de fecha y hora:", font=("Helvetica", 12), bg="#34495E", fg="white")
    hora_label.pack(side='left', padx=5)

    hora_entry = tk.Entry(hora_frame, width=40, font=("Helvetica", 12))
    hora_entry.pack(side='left', padx=5)
    hora_entry.insert(0, '11:29:31 p. m. 27/09/2024.2')  # Valor por defecto

    # Botón para procesar datos
    process_button = tk.Button(root, text="Procesar Datos", font=("Helvetica", 12), command=procesar_datos,
                               bg="#E67E22", fg="white", padx=10, pady=5)
    process_button.pack(pady=10)

    # Iniciar la aplicación
    root.mainloop()

if __name__ == "__main__":
    crear_interfaz()