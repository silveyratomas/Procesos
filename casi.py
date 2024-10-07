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
procesos_nuevos = []
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
        self.estado = 'Nuevos'
        self.veces_bloqueado = 0  # Nuevo atributo para contar las veces que ha sido bloqueado

    def __str__(self):
        return f"Proceso {self.id}: {self.estado} (Memoria: {self.memoria} MB)"

# Función para crear procesos aleatorios
def crear_procesos_automaticos():
    while True:
        if len(procesos) < 30:  # Máximo 30 procesos simultáneos
            memoria_necesaria = random.randint(50, 200)
            agregar_proceso(memoria_necesaria)
        time.sleep(4)

# Función para agregar un proceso (manual o aleatorio)
def agregar_proceso(memoria_necesaria):
    global MEMORIA_USADA
    proceso = Proceso(len(procesos) + 1, memoria_necesaria)
    
    # Agrega el proceso que se creó a "NUEVO" y a "PROCESOS"
    if MEMORIA_USADA + memoria_necesaria <= MEMORIA_TOTAL:
        procesos_nuevos.append(proceso)
        proceso.estado = 'Nuevos'
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

def nuevo_a_listo():
    global MEMORIA_USADA
    while True:
        for proceso in procesos_nuevos[:]:
            if MEMORIA_USADA + proceso.memoria <= MEMORIA_TOTAL:
                procesos_nuevos.remove(proceso)
                procesos_listos.append(proceso)
                proceso.estado = 'Listo'
                MEMORIA_USADA += proceso.memoria  # Solo suma cuando entra a Listo
                actualizar_interfaz()
            else:
                mensaje_error.config(text="Memoria insuficiente. El proceso se mantiene en Nuevos.")
        time.sleep(3)

# Función para mover el proceso con la menor memoria de bloqueado a listo
def mover_a_listo_menor_memoria():
    global MEMORIA_USADA

    if procesos_bloqueados:
        proceso_menor_memoria = min(procesos_bloqueados, key=lambda p: p.memoria)
        procesos_bloqueados.remove(proceso_menor_memoria)
        procesos_listos.append(proceso_menor_memoria)
        proceso_menor_memoria.estado = 'Listo'
        actualizar_interfaz()

def mover_a_listo_mayor_memoria():
    global MEMORIA_USADA

    if procesos_bloqueados:
        proceso_mayor_memoria = max(procesos_bloqueados, key=lambda p: p.memoria)
        procesos_bloqueados.remove(proceso_mayor_memoria)
        procesos_listos.append(proceso_mayor_memoria)
        proceso_mayor_memoria.estado = 'Listo'
        actualizar_interfaz()

# Función para mover procesos bloqueados a listos periódicamente
def mover_bloqueados_a_listos():
    while True:
        time.sleep(3)  # Cada 3 segundos
        mover_a_listo_menor_memoria()  # Intenta mover el proceso con la menor memoria a listo
        time.sleep(6) # Cada 6 segundos
        mover_a_listo_mayor_memoria() # Intenta mover el proceso con la mayor memoria a listo

# Función para mover bloqueados a swap
def mover_a_swap(proceso):
    global MEMORIA_USADA
    if proceso in procesos_bloqueados:
        procesos_bloqueados.remove(proceso)
        procesos_swap.append(proceso)
        proceso.estado = 'Swap'
        MEMORIA_USADA -= proceso.memoria  # Restar memoria solo cuando sale de bloqueado
        actualizar_interfaz()

# Define la probabilidad de mover procesos de swap a bloqueados
PROBABILIDAD_SWAP_A_BLOQUEADO = 0.3  # 30% de probabilidad
# Función para revisar procesos en Swap y moverlos a Listos o Bloqueados si hay suficiente memoria
def revisar_swap():
    global MEMORIA_USADA
    while True:
        for proceso in procesos_swap[:]:
            if MEMORIA_USADA + proceso.memoria <= MEMORIA_TOTAL and random.random() < PROBABILIDAD_SWAP_A_BLOQUEADO:
                procesos_swap.remove(proceso)
                procesos_bloqueados.append(proceso)
                proceso.estado = 'Bloqueado'
                MEMORIA_USADA += proceso.memoria
                mensaje_error.config(text=f"El Proceso {proceso.id} se ha movido a Bloqueado desde Swap.")
            else:
                if MEMORIA_USADA + proceso.memoria <= MEMORIA_TOTAL:
                    procesos_swap.remove(proceso)
                    procesos_listos.append(proceso)
                    proceso.estado = 'Listo'
                    MEMORIA_USADA += proceso.memoria
                    mensaje_error.config(text=f"El Proceso {proceso.id} ha pasado a Listo desde Swap.")
                    
            actualizar_interfaz()
        time.sleep(7)

# Define la probabilidad de que un proceso en ejecución pase a bloqueado
PROBABILIDAD_BLOQUEO = 0.9  # 90% de probabilidad de que un proceso pase a bloqueado
# Define la probabilidad de que un proceso en listo pase a swap en lugar de ejecutarse
PROBABILIDAD_LISTO_A_SWAP = 0.2  # 20% de probabilidad
PROBABILIDAD_EJECUTANDO_A_SWAP = 0.2  # 20% de probabilidad

# Función para simular la ejecución de procesos
def ejecutar_procesos():
    global MEMORIA_USADA, proceso_ejecucion
    while True:
        if procesos_listos:
            proceso_ejecucion = procesos_listos.pop(0)  # FIFO, obtenemos el primer proceso listo
            
            # Verificar si el proceso se mueve a Swap
            if random.random() < PROBABILIDAD_LISTO_A_SWAP and len(procesos_swap) < MAX_SWAP:
                proceso_ejecucion.estado = 'Swap'
                procesos_swap.append(proceso_ejecucion)
                mensaje_error.config(text=f"El Proceso {proceso_ejecucion.id} se ha movido a Swap desde Listos.")
                MEMORIA_USADA -= proceso_ejecucion.memoria
            else:
                proceso_ejecucion.estado = 'Ejecutando'
                actualizar_interfaz()
                time.sleep(3)  # Simula el tiempo de ejecución del proceso

                # Ajustar la probabilidad de bloqueo
                if proceso_ejecucion.veces_bloqueado > 0:
                    probabilidad_bloqueo_actual = 0.1
                else:
                    probabilidad_bloqueo_actual = PROBABILIDAD_BLOQUEO

                # Simular el bloqueo del proceso
                if random.random() < probabilidad_bloqueo_actual:
                    proceso_ejecucion.estado = 'Bloqueado'
                    procesos_bloqueados.append(proceso_ejecucion)
                    proceso_ejecucion.veces_bloqueado += 1  # Incrementar el contador de bloqueos
                    mensaje_error.config(text=f"El Proceso {proceso_ejecucion.id} se ha bloqueado durante la ejecución.")
                elif random.random() < PROBABILIDAD_EJECUTANDO_A_SWAP and len(procesos_swap) < MAX_SWAP:
                    proceso_ejecucion.estado = 'Swap'
                    procesos_swap.append(proceso_ejecucion)
                    mensaje_error.config(text=f"El Proceso {proceso_ejecucion.id} se ha suspendido durante la ejecución.")
                    MEMORIA_USADA -= proceso_ejecucion.memoria
                else:
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

# Función para agregar un proceso aleatorio
def agregar_proceso_aleatorio():
    memoria_necesaria = random.randint(50, 200)
    agregar_proceso(memoria_necesaria)

# Función para actualizar la interfaz gráfica
def actualizar_interfaz():
    memoria_label.config(text=f"Memoria Usada: {MEMORIA_USADA}/{MEMORIA_TOTAL} MB")
    
    # Limpiar y actualizar lista de procesos
    nuevos_listbox.delete(0, tk.END)
    for p in procesos_nuevos:
        nuevos_listbox.insert(tk.END, str(p))

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

    ejecucion_label.config(text=f"{proceso_ejecucion if proceso_ejecucion else ''}")
    mensaje_error.config(text="")  # Limpiar mensaje de error en cada actualización

    # Mostrar procesos en memoria
    mostrar_procesos_en_memoria()

def mostrar_procesos_en_memoria():
    # Limpiar el canvas
    canvas.delete("all")
    
    # Calcular posiciones para los bloques de memoria
    x_offset = 10
    y_offset = 10
    block_width = 30
    block_height = 50
    spacing = 5
    
    # Dibujar bloques de memoria
    for i in range(MEMORIA_TOTAL // 50):  # Supongamos que cada bloque representa 50 MB
        color = "white"  # Color por defecto para bloques vacíos
        pid = ""

        for proceso in procesos_listos + procesos_bloqueados + procesos_swap:  # Revisa todos los estados
            if i * 50 < MEMORIA_USADA:  # Si la posición está ocupada
                color = "lightgreen" if proceso.estado == "Listo" else "lightcoral" if proceso.estado == "Bloqueado" else "lightblue"
                pid = proceso.id
                break  # Salir una vez que se haya encontrado un proceso

        # Dibujar el bloque de memoria
        canvas.create_rectangle(x_offset + (i * (block_width + spacing)), y_offset, 
                                x_offset + (i * (block_width + spacing)) + block_width, 
                                y_offset + block_height, fill=color, outline="black")
        
        # Dibujar el PID si hay un proceso en ese bloque
        if pid:
            canvas.create_text(x_offset + (i * (block_width + spacing)) + block_width / 2, 
                               y_offset + block_height / 2, text=pid, fill="black")

# Configuración de la interfaz gráfica con Tkinter
ventana = tk.Tk()
ventana.title("Simulador de Gestión de Procesos y Memoria")
ventana.geometry("800x600")
ventana.config(bg="#f0f0f0")

# Sección para mostrar el uso de memoria
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

# Sección para mostrar el canvas de memoria
canvas = tk.Canvas(ventana, width=600, height=200, bg="white")
canvas.pack(pady=20)

# Listas para mostrar el estado de los procesos
frame_listas = tk.Frame(ventana, pady=10, bg="#f0f0f0")
frame_listas.pack(fill=tk.BOTH, expand=True)

# Listas de procesos
nuevos_listbox = tk.Listbox(frame_listas, bg="#e0ffff", height=8, font=("Arial", 10))
nuevos_listbox.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)

listos_listbox = tk.Listbox(frame_listas, bg="#add8e6", height=8, font=("Arial", 10))
listos_listbox.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)

bloqueados_listbox = tk.Listbox(frame_listas, bg="#ffcccb", height=8, font=("Arial", 10))
bloqueados_listbox.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)

swap_listbox = tk.Listbox(frame_listas, bg="#ffebcd", height=8, font=("Arial", 10))
swap_listbox.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)

terminados_listbox = tk.Listbox(frame_listas, bg="#d3d3d3", height=8, font=("Arial", 10))
terminados_listbox.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)

# Etiqueta para mostrar el proceso en ejecución
ejecucion_label = tk.Label(ventana, text="", font=("Arial", 12, "bold"), bg="#f0f0f0")
ejecucion_label.pack(pady=10)

# Inicialización de hilos
hilo_ejecucion = threading.Thread(target=ejecutar_procesos)
hilo_ejecucion.start()

hilo_bloqueados = threading.Thread(target=mover_bloqueados_a_listos)
hilo_bloqueados.start()

hilo_nuevolisto = threading.Thread(target=nuevo_a_listo)
hilo_nuevolisto.start()

hilo_swap = threading.Thread(target=revisar_swap)
hilo_swap.start()

# Hilo para crear procesos aleatorios
hilo_procesos_aleatorios = threading.Thread(target=crear_procesos_automaticos)
hilo_procesos_aleatorios.start()

# Hilo principal que se encarga de actualizar la interfaz
ventana.mainloop()
