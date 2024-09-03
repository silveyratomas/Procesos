import tkinter as tk
import random
import threading
import time

# Configuración de la memoria
MEMORIA_TOTAL = 1000  # Memoria total disponible (en MB)
MEMORIA_USADA = 0  # Memoria actualmente en uso (en MB)
MAX_SWAP = 10  # Máximo número de procesos en swap

# Lista de procesos en diferentes estados
procesos = []
procesos_listos = []
procesos_bloqueados = []
procesos_swap = []
procesos_terminados = []
proceso_ejecucion = None

# Clase para representar un proceso
class Proceso:
    def __init__(self, id, memoria):
        self.id = id
        self.memoria = memoria
        self.estado = 'Listo'

    def __str__(self):
        return f"Proceso {self.id}: {self.estado} (Memoria: {self.memoria} MB)"

# Función para crear procesos aleatorios
def crear_procesos_automaticos():
    while True:
        if len(procesos) < 10:  # Máximo 10 procesos simultáneos
            memoria_necesaria = random.randint(50, 200)
            agregar_proceso(memoria_necesaria)
        time.sleep(2)

# Función para agregar un proceso (manual o aleatorio)
def agregar_proceso(memoria_necesaria):
    global MEMORIA_USADA
    proceso = Proceso(len(procesos) + 1, memoria_necesaria)

    # Mueve procesos bloqueados a swap para dar espacio al nuevo proceso
    while procesos_bloqueados and MEMORIA_USADA + memoria_necesaria > MEMORIA_TOTAL:
        mover_a_swap(procesos_bloqueados[0])

    if MEMORIA_USADA + memoria_necesaria <= MEMORIA_TOTAL:
        if random.random() <= 0.45:  # 45% de probabilidad de ir a bloqueado
            procesos_bloqueados.append(proceso)
            proceso.estado = 'Bloqueado'
        else:
            procesos_listos.append(proceso)
            proceso.estado = 'Listo'
            MEMORIA_USADA += memoria_necesaria
    else:
        # Mostrar mensaje de error y enviar proceso al swap si supera la memoria total
        mensaje_error.config(text="Se superó el máximo de memoria, proceso enviado a swap.")
        mover_a_swap_directo(proceso)

    procesos.append(proceso)
    actualizar_interfaz()

# Función para mover un proceso directamente al swap
def mover_a_swap_directo(proceso):
    global MEMORIA_USADA
    if len(procesos_swap) < MAX_SWAP:
        procesos_swap.append(proceso)
        proceso.estado = 'Swap'
        actualizar_interfaz()
    else:
        # Se queda bloqueado si no hay espacio en swap
        proceso.estado = 'Bloqueado'
        procesos_bloqueados.append(proceso)
        actualizar_interfaz()

# Función para mover un proceso de bloqueado a listo
def mover_a_listo(proceso):
    global MEMORIA_USADA
    if proceso in procesos_bloqueados:
        procesos_bloqueados.remove(proceso)
        procesos_listos.append(proceso)
        proceso.estado = 'Listo'
        MEMORIA_USADA += proceso.memoria
        actualizar_interfaz()

# Función para mover procesos bloqueados a listos periódicamente
def mover_bloqueados_a_listos():
    global MEMORIA_USADA
    while True:
        time.sleep(10)  # Cada 10 segundos
        for proceso in procesos_bloqueados[:]:
            if MEMORIA_USADA + proceso.memoria <= MEMORIA_TOTAL:
                mover_a_listo(proceso)
        actualizar_interfaz()

# Función para mover procesos a swap
def mover_a_swap(proceso):
    global MEMORIA_USADA
    if len(procesos_swap) < MAX_SWAP:
        procesos_bloqueados.remove(proceso)
        procesos_swap.append(proceso)
        proceso.estado = 'Swap'
        MEMORIA_USADA -= proceso.memoria  # Libera memoria de bloqueados
        actualizar_interfaz()
    else:
        # Se queda en bloqueados si no hay espacio en swap
        proceso.estado = 'Bloqueado'
        actualizar_interfaz()

# Función para revisar procesos en Swap y moverlos a Listos si hay suficiente memoria
def revisar_swap():
    global MEMORIA_USADA
    while True:
        for proceso in procesos_swap[:]:
            if MEMORIA_USADA + proceso.memoria <= MEMORIA_TOTAL:
                procesos_swap.remove(proceso)
                procesos_listos.append(proceso)
                proceso.estado = 'Listo'
                MEMORIA_USADA += proceso.memoria
                actualizar_interfaz()
        time.sleep(1)

# Función para simular la ejecución de procesos
def ejecutar_procesos():
    global MEMORIA_USADA, proceso_ejecucion
    while True:
        if procesos_listos:
            proceso_ejecucion = procesos_listos.pop(0)
            proceso_ejecucion.estado = 'Ejecutando'
            actualizar_interfaz()
            time.sleep(3)  # Simula el tiempo de ejecución del proceso
            proceso_ejecucion.estado = 'Terminado'
            procesos_terminados.append(proceso_ejecucion)
            MEMORIA_USADA -= proceso_ejecucion.memoria
            proceso_ejecucion = None
        actualizar_interfaz()
        time.sleep(1)

# Función para manejar el evento de agregar un proceso manualmente
def agregar_proceso_manual():
    try:
        memoria_necesaria = int(memoria_entry.get())
        if memoria_necesaria > 0:
            agregar_proceso(memoria_necesaria)
        else:
            tk.messagebox.showerror("Error", "La memoria debe ser un número positivo.")
    except ValueError:
        tk.messagebox.showerror("Error", "Ingrese un valor numérico válido para la memoria.")
    finally:
        memoria_entry.delete(0, tk.END)  # Limpiar el campo de entrada

# Función para agregar un proceso aleatorio desde el botón
def agregar_proceso_aleatorio():
    memoria_necesaria = random.randint(50, 200)
    agregar_proceso(memoria_necesaria)

# Actualiza la interfaz gráfica
def actualizar_interfaz():
    memoria_label.config(text=f"Memoria Usada: {MEMORIA_USADA}/{MEMORIA_TOTAL} MB")
    listos_listbox.delete(0, tk.END)
    for p in procesos_listos:
        listos_listbox.insert(tk.END, str(p))
    bloqueados_listbox.delete(0, tk.END)
    for p in procesos_bloqueados:
        bloqueados_listbox.insert(tk.END, str(p))
    swap_listbox.delete(0, tk.END)
    for p in procesos_swap:
        swap_listbox.insert(tk.END, str(p))
    terminados_listbox.delete(0, tk.END)
    for p in procesos_terminados:
        terminados_listbox.insert(tk.END, str(p))
    ejecucion_label.config(text=f"Proceso en Ejecución: {proceso_ejecucion if proceso_ejecucion else 'Ninguno'}")
    mensaje_error.config(text="")  # Limpiar mensaje de error en cada actualización

# Configuración de la interfaz gráfica con Tkinter
ventana = tk.Tk()
ventana.title("Simulador de Gestión de Procesos y Memoria")
ventana.geometry("800x600")
ventana.config(bg="#f0f0f0")

# Sección superior para mostrar el uso de memoria
frame_memoria = tk.Frame(ventana, pady=10, bg="#f0f0f0")
frame_memoria.pack(fill=tk.X)

memoria_label = tk.Label(frame_memoria, text=f"Memoria Usada: {MEMORIA_USADA}/{MEMORIA_TOTAL} MB", font=("Arial", 14, "bold"), bg="#f0f0f0")
memoria_label.pack()

# Sección para agregar procesos manualmente y aleatoriamente
frame_agregar = tk.Frame(ventana, pady=10, padx=10, bd=2, relief=tk.RAISED, bg="#dcdcdc")
frame_agregar.pack(fill=tk.X, pady=10)

memoria_label_entry = tk.Label(frame_agregar, text="Memoria del Proceso (MB):", font=("Arial", 12), bg="#dcdcdc")
memoria_label_entry.pack(side=tk.LEFT)

memoria_entry = tk.Entry(frame_agregar, width=10, font=("Arial", 12))
memoria_entry.pack(side=tk.LEFT, padx=5)

agregar_boton = tk.Button(frame_agregar, text="Agregar Proceso", command=agregar_proceso_manual, font=("Arial", 12), bg="#90ee90")
agregar_boton.pack(side=tk.LEFT, padx=5)

# Botón para agregar proceso aleatorio
agregar_aleatorio_boton = tk.Button(frame_agregar, text="Agregar Proceso Aleatorio", command=agregar_proceso_aleatorio, font=("Arial", 12), bg="#add8e6")
agregar_aleatorio_boton.pack(side=tk.LEFT, padx=5)

# Mensaje de error si se supera la memoria
mensaje_error = tk.Label(frame_agregar, text="", font=("Arial", 12), fg="red", bg="#dcdcdc")
mensaje_error.pack(side=tk.LEFT, padx=10)

# Sección para mostrar la lista de procesos en diferentes estados
frame_procesos = tk.Frame(ventana, padx=10, pady=10, bg="#f0f0f0")
frame_procesos.pack(fill=tk.BOTH, expand=True)

# Sección de procesos listos
frame_listos = tk.Frame(frame_procesos, padx=10, pady=10, bd=2, relief=tk.SUNKEN, bg="#f0f0f0")
frame_listos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

listos_label = tk.Label(frame_listos, text="Procesos Listos", font=("Arial", 14, "bold"), bg="#f0f0f0")
listos_label.pack()

listos_listbox = tk.Listbox(frame_listos, font=("Arial", 12), bg="#e0f7fa")
listos_listbox.pack(fill=tk.BOTH, expand=True)

# Sección de procesos bloqueados
frame_bloqueados = tk.Frame(frame_procesos, padx=10, pady=10, bd=2, relief=tk.SUNKEN, bg="#f0f0f0")
frame_bloqueados.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

bloqueados_label = tk.Label(frame_bloqueados, text="Procesos Bloqueados", font=("Arial", 14, "bold"), bg="#f0f0f0")
bloqueados_label.pack()

bloqueados_listbox = tk.Listbox(frame_bloqueados, font=("Arial", 12), bg="#ffe0b2")
bloqueados_listbox.pack(fill=tk.BOTH, expand=True)

# Sección de procesos en swap
frame_swap = tk.Frame(frame_procesos, padx=10, pady=10, bd=2, relief=tk.SUNKEN, bg="#f0f0f0")
frame_swap.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

swap_label = tk.Label(frame_swap, text="Procesos en Swap", font=("Arial", 14, "bold"), bg="#f0f0f0")
swap_label.pack()

swap_listbox = tk.Listbox(frame_swap, font=("Arial", 12), bg="#f8bbd0")
swap_listbox.pack(fill=tk.BOTH, expand=True)

# Sección de procesos terminados
frame_terminados = tk.Frame(frame_procesos, padx=10, pady=10, bd=2, relief=tk.SUNKEN, bg="#f0f0f0")
frame_terminados.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

terminados_label = tk.Label(frame_terminados, text="Procesos Terminados", font=("Arial", 14, "bold"), bg="#f0f0f0")
terminados_label.pack()

terminados_listbox = tk.Listbox(frame_terminados, font=("Arial", 12), bg="#c8e6c9")
terminados_listbox.pack(fill=tk.BOTH, expand=True)

# Sección para mostrar el proceso en ejecución
frame_ejecucion = tk.Frame(ventana, pady=10, bg="#f0f0f0")
frame_ejecucion.pack(fill=tk.X)

ejecucion_label = tk.Label(frame_ejecucion, text="Proceso en Ejecución: Ninguno", font=("Arial", 14, "bold"), bg="#f0f0f0")
ejecucion_label.pack()

# Función para finalizar la simulación
def finalizar_simulacion():
    ventana.quit()

# Botón para finalizar la simulación
finalizar_boton = tk.Button(ventana, text="Finalizar Simulación", command=finalizar_simulacion, font=("Arial", 14), bg="#ff6f61")
finalizar_boton.pack(side=tk.BOTTOM, pady=10)

# Inicialización de hilos
hilo_ejecucion = threading.Thread(target=ejecutar_procesos)
hilo_ejecucion.start()

hilo_bloqueados = threading.Thread(target=mover_bloqueados_a_listos)
hilo_bloqueados.start()

hilo_swap = threading.Thread(target=revisar_swap)
hilo_swap.start()

# Hilo para crear procesos aleatorios
hilo_procesos_aleatorios = threading.Thread(target=crear_procesos_automaticos)
hilo_procesos_aleatorios.start()

ventana.mainloop()
