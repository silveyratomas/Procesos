import tkinter as tk
import random
import threading
import time

# Configuración de la memoria
MEMORIA_TOTAL = 1000  # Memoria total disponible (en MB)
MEMORIA_USADA = 0  # Memoria actualmente en uso (en MB)

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
def crear_procesos():
    while True:
        if len(procesos) < 10:  # Máximo 10 procesos simultáneos
            memoria_necesaria = random.randint(50, 200)
            agregar_proceso(memoria_necesaria)
        time.sleep(2)

# Función para agregar un proceso (manual o aleatorio)
def agregar_proceso(memoria_necesaria):
    global MEMORIA_USADA
    proceso = Proceso(len(procesos) + 1, memoria_necesaria)

    if MEMORIA_USADA + memoria_necesaria <= MEMORIA_TOTAL:
        procesos_listos.append(proceso)
        MEMORIA_USADA += memoria_necesaria
        proceso.estado = 'Listo'
    else:
        proceso.estado = 'Swap'
        procesos_swap.append(proceso)

    procesos.append(proceso)
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

# Configuración de la interfaz gráfica con Tkinter
ventana = tk.Tk()
ventana.title("Simulador de Gestión de Procesos y Memoria")
ventana.geometry("600x500")

# Sección superior para mostrar el uso de memoria
frame_memoria = tk.Frame(ventana, pady=10)
frame_memoria.pack(fill=tk.X)

memoria_label = tk.Label(frame_memoria, text=f"Memoria Usada: {MEMORIA_USADA}/{MEMORIA_TOTAL} MB", font=("Arial", 12))
memoria_label.pack()

# Sección para agregar procesos manualmente
frame_agregar = tk.Frame(ventana, pady=10, padx=10, bd=2, relief=tk.GROOVE)
frame_agregar.pack(fill=tk.X, pady=10)

memoria_label_entry = tk.Label(frame_agregar, text="Memoria del Proceso (MB):", font=("Arial", 10))
memoria_label_entry.pack(side=tk.LEFT)

memoria_entry = tk.Entry(frame_agregar, width=10, font=("Arial", 10))
memoria_entry.pack(side=tk.LEFT, padx=5)

agregar_boton = tk.Button(frame_agregar, text="Agregar Proceso", command=agregar_proceso_manual, font=("Arial", 10))
agregar_boton.pack(side=tk.LEFT, padx=5)

# Sección principal para mostrar los procesos
frame_procesos = tk.Frame(ventana, padx=10, pady=10)
frame_procesos.pack(fill=tk.BOTH, expand=True)

# Procesos Listos
frame_listos = tk.Frame(frame_procesos, bd=2, relief=tk.GROOVE)
frame_listos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

listos_label = tk.Label(frame_listos, text="Procesos Listos", font=("Arial", 12))
listos_label.pack(pady=5)

listos_listbox = tk.Listbox(frame_listos, font=("Arial", 10), height=8)
listos_listbox.pack(fill=tk.BOTH, expand=True)

# Proceso en Ejecución
frame_ejecucion = tk.Frame(frame_procesos, bd=2, relief=tk.GROOVE)
frame_ejecucion.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

ejecucion_label = tk.Label(frame_ejecucion, text="Proceso en Ejecución: Ninguno", font=("Arial", 12))
ejecucion_label.pack(pady=5)

# Procesos Bloqueados
frame_bloqueados = tk.Frame(frame_procesos, bd=2, relief=tk.GROOVE)
frame_bloqueados.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

bloqueados_label = tk.Label(frame_bloqueados, text="Procesos Bloqueados", font=("Arial", 12))
bloqueados_label.pack(pady=5)

bloqueados_listbox = tk.Listbox(frame_bloqueados, font=("Arial", 10), height=8)
bloqueados_listbox.pack(fill=tk.BOTH, expand=True)

# Procesos en Swap
frame_swap = tk.Frame(frame_procesos, bd=2, relief=tk.GROOVE)
frame_swap.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

swap_label = tk.Label(frame_swap, text="Procesos en Swap", font=("Arial", 12))
swap_label.pack(pady=5)

swap_listbox = tk.Listbox(frame_swap, font=("Arial", 10), height=8)
swap_listbox.pack(fill=tk.BOTH, expand=True)

# Procesos Terminados
frame_terminados = tk.Frame(ventana, bd=2, relief=tk.GROOVE)
frame_terminados.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)

terminados_label = tk.Label(frame_terminados, text="Procesos Terminados", font=("Arial", 12))
terminados_label.pack(pady=5)

terminados_listbox = tk.Listbox(frame_terminados, font=("Arial", 10), height=8)
terminados_listbox.pack(fill=tk.BOTH, expand=True)

# Hilos para la simulación de creación, ejecución de procesos y revisión de Swap
creador_procesos_thread = threading.Thread(target=crear_procesos, daemon=True)
ejecutor_procesos_thread = threading.Thread(target=ejecutar_procesos, daemon=True)
revisor_swap_thread = threading.Thread(target=revisar_swap, daemon=True)

creador_procesos_thread.start()
ejecutor_procesos_thread.start()
revisor_swap_thread.start()

ventana.mainloop()
