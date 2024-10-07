import tkinter as tk
import random
import threading
import time

# Configuración de la memoria
MEMORIA_TOTAL = 1000  # Memoria total disponible (en MB)
MEMORIA_USADA = 0  # Memoria actualmente en uso (en MB)
MAX_SWAP = 5  # Máximo número de procesos en swap
TAMANO_PAGINA = 50  # Tamaño de cada página en MB
NUMERO_PAGINAS = MEMORIA_TOTAL // TAMANO_PAGINA  # Cantidad total de páginas en memoria
paginas_memoria = [None] * NUMERO_PAGINAS  # Tabla de páginas para la memoria

# Lista de procesos en diferentes estados
procesos = []
procesos_nuevos = []
procesos_listos = []
procesos_bloqueados = []
procesos_swap = []
procesos_terminados = []
recursos = []
proceso_ejecucion = None

# Clase para representar un proceso
class Proceso:
    def __init__(self, id, memoria):
        self.id = id
        self.memoria = memoria
        self.estado = 'Nuevos'
        self.veces_bloqueado = 0  # Nuevo atributo para contar las veces que ha sido bloqueado
        self.recurso = random.randint(0, 2)
        self.paginas = []  # Páginas asignadas en la memoria principal

    def __str__(self):
        return f"Proceso {self.id}: {self.estado} (Memoria: {self.memoria} MB) Recurso: {self.recurso}"
        

# Función para asignar páginas a un proceso en la memoria
def asignar_paginas(proceso):
    global MEMORIA_USADA
    paginas_necesarias = (proceso.memoria + TAMANO_PAGINA - 1) // TAMANO_PAGINA  # Redondeo hacia arriba

    if paginas_memoria.count(None) >= paginas_necesarias: #si 
        for i in range(NUMERO_PAGINAS):
            if len(proceso.paginas) == paginas_necesarias:
                break
            if paginas_memoria[i] is None:
                paginas_memoria[i] = proceso.id
                proceso.paginas.append(i)
                MEMORIA_USADA += TAMANO_PAGINA

        return True
    else:
        return False

# Función para liberar las páginas asignadas a un proceso
def liberar_paginas(proceso):
    global MEMORIA_USADA
    for pagina in proceso.paginas:
        paginas_memoria[pagina] = None
        MEMORIA_USADA -= TAMANO_PAGINA
    proceso.paginas = []

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
    
    if asignar_paginas(proceso):
        procesos_nuevos.append(proceso)
        proceso.estado = 'Nuevos'
        procesos.append(proceso)
    else:
        mensaje_error.config(text="Memoria insuficiente para el nuevo proceso.")

    actualizar_interfaz()

# Función para mover un proceso directamente al swap
def mover_a_swap_directo(proceso):
    if len(procesos_swap) < MAX_SWAP:
        liberar_paginas(proceso)
        procesos_swap.append(proceso)
        proceso.estado = 'Swap'
        actualizar_interfaz()
    else:
        proceso.estado = 'Bloqueado'
        procesos_bloqueados.append(proceso)
        actualizar_interfaz()

def nuevo_a_listo():
    global MEMORIA_USADA
    while True:
        for proceso in procesos_nuevos[:]:
            if asignar_paginas(proceso):
                procesos_nuevos.remove(proceso)
                procesos_listos.append(proceso)
                proceso.estado = 'Listo'
                actualizar_interfaz()
            else:
                mensaje_error.config(text="Memoria insuficiente. El proceso se mantiene en Nuevos.")
        time.sleep(3)

# Función para mover el proceso con la menor memoria de bloqueado a listo
def mover_a_listo_menor_memoria():
    if procesos_bloqueados:
        proceso_menor_memoria = min(procesos_bloqueados, key=lambda p: p.memoria)
        if asignar_paginas(proceso_menor_memoria):
            procesos_bloqueados.remove(proceso_menor_memoria)
            procesos_listos.append(proceso_menor_memoria)
            proceso_menor_memoria.estado = 'Listo'
            actualizar_interfaz()

def mover_a_listo_mayor_memoria():
    if procesos_bloqueados:
        proceso_mayor_memoria = max(procesos_bloqueados, key=lambda p: p.memoria)
        if asignar_paginas(proceso_mayor_memoria):
            procesos_bloqueados.remove(proceso_mayor_memoria)
            procesos_listos.append(proceso_mayor_memoria)
            proceso_mayor_memoria.estado = 'Listo'
            actualizar_interfaz()

# Función para mover procesos bloqueados a listos periódicamente
def mover_bloqueados_a_listos():
    while True:
        time.sleep(3)  # Cada 3 segundos
        mover_a_listo_menor_memoria()  # Intenta mover el proceso con la menor memoria a listo
        time.sleep(6)  # Cada 6 segundos
        mover_a_listo_mayor_memoria()  # Intenta mover el proceso con la mayor memoria a listo

# Función para mover bloqueados a swap
def mover_a_swap(proceso):
    if proceso in procesos_bloqueados:
        liberar_paginas(proceso)
        procesos_bloqueados.remove(proceso)
        procesos_swap.append(proceso)
        proceso.estado = 'Swap'
        actualizar_interfaz()

# Función para revisar procesos en Swap y moverlos a Listos o Bloqueados si hay suficiente memoria
def revisar_swap():
    while True:
        for proceso in procesos_swap[:]:
            if asignar_paginas(proceso):
                procesos_swap.remove(proceso)
                procesos_listos.append(proceso)
                proceso.estado = 'Listo'
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

    # Dibujar las páginas de memoria
    for i in range(NUMERO_PAGINAS):
        x0, y0 = (i % 10) * 50, (i // 10) * 50
        x1, y1 = x0 + 40, y0 + 40
        proceso_id = paginas_memoria[i]
        color = "lightgreen" if proceso_id else "white"
        canvas.create_rectangle(x0, y0, x1, y1, fill=color)
        if proceso_id:
            canvas.create_text((x0 + 20, y0 + 20), text=str(proceso_id))

# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Simulador de Gestión de Procesos y Memoria")

# Secciones para diferentes procesos
tk.Label(root, text="Procesos Nuevos").grid(row=0, column=0)
nuevos_listbox = tk.Listbox(root)
nuevos_listbox.grid(row=1, column=0)

tk.Label(root, text="Procesos Listos").grid(row=0, column=1)
listos_listbox = tk.Listbox(root)
listos_listbox.grid(row=1, column=1)

tk.Label(root, text="Procesos Bloqueados").grid(row=0, column=2)
bloqueados_listbox = tk.Listbox(root)
bloqueados_listbox.grid(row=1, column=2)

tk.Label(root, text="Procesos en Swap").grid(row=0, column=3)
swap_listbox = tk.Listbox(root)
swap_listbox.grid(row=1, column=3)

tk.Label(root, text="Procesos Terminados").grid(row=0, column=4)
terminados_listbox = tk.Listbox(root)
terminados_listbox.grid(row=1, column=4)

tk.Label(root, text="Proceso en Ejecución").grid(row=2, column=0, columnspan=5)
ejecucion_label = tk.Label(root, text="")
ejecucion_label.grid(row=3, column=0, columnspan=5)

# Entrada para agregar procesos manualmente
tk.Label(root, text="Memoria del proceso (MB):").grid(row=4, column=0)
memoria_entry = tk.Entry(root)
memoria_entry.grid(row=4, column=1)

tk.Button(root, text="Agregar Proceso", command=agregar_proceso_manual).grid(row=4, column=2)

# Botón para agregar un proceso aleatorio
tk.Button(root, text="Agregar Proceso Aleatorio", command=agregar_proceso_aleatorio).grid(row=4, column=3)

# Mensaje de error
mensaje_error = tk.Label(root, text="", fg="red")
mensaje_error.grid(row=5, column=0, columnspan=5)

# Indicador de memoria
memoria_label = tk.Label(root, text=f"Memoria Usada: {MEMORIA_USADA}/{MEMORIA_TOTAL} MB")
memoria_label.grid(row=6, column=0, columnspan=5)

# Canvas para mostrar las páginas de memoria
canvas = tk.Canvas(root, width=500, height=300)
canvas.grid(row=7, column=0, columnspan=5)

# Hilos para las diferentes tareas de fondo
threading.Thread(target=crear_procesos_automaticos, daemon=True).start()
threading.Thread(target=ejecutar_procesos, daemon=True).start()
threading.Thread(target=nuevo_a_listo, daemon=True).start()
threading.Thread(target=revisar_swap, daemon=True).start()
threading.Thread(target=mover_bloqueados_a_listos, daemon=True).start()

# Iniciar el loop de la interfaz gráfica
root.mainloop()
