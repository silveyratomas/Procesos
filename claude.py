import tkinter as tk
from tkinter import ttk
import random
import time
from threading import Thread, Lock

class Proceso:
    def __init__(self, id, tamanio):
        self.id = id
        self.tamanio = tamanio
        self.estado = "Nuevo"
        self.paginas = []

class SimuladorProcesos:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Gestión de Procesos y Memoria")
        
        self.memoria_total = 1000
        self.memoria_disponible = self.memoria_total
        self.tamanio_pagina = 100
        self.procesos = []
        self.cola_nuevos = []
        self.cola_listos = []
        self.proceso_ejecutando = None
        self.tabla_paginas = {}
        self.recurso_compartido = Lock()
        
        self.setup_ui()
        
        self.thread = Thread(target=self.ejecutar_simulacion)
        self.thread.start()
    
    def setup_ui(self):
        # Configuración de la interfaz gráfica aquí...
        pass
    
    def crear_proceso(self):
        id = len(self.procesos) + 1
        tamanio = random.randint(50, 300)
        proceso = Proceso(id, tamanio)
        self.procesos.append(proceso)
        self.cola_nuevos.append(proceso)
    
    def asignar_memoria(self, proceso):
        if self.memoria_disponible >= proceso.tamanio:
            paginas_necesarias = (proceso.tamanio + self.tamanio_pagina - 1) // self.tamanio_pagina
            paginas_asignadas = []
            for _ in range(paginas_necesarias):
                pagina = self.encontrar_pagina_libre()
                if pagina is not None:
                    paginas_asignadas.append(pagina)
                else:
                    # No hay suficientes páginas libres, liberar las asignadas
                    for p in paginas_asignadas:
                        self.liberar_pagina(p)
                    return False
            proceso.paginas = paginas_asignadas
            self.tabla_paginas[proceso.id] = paginas_asignadas
            self.memoria_disponible -= proceso.tamanio
            return True
        return False
    
    def encontrar_pagina_libre(self):
        for i in range(self.memoria_total // self.tamanio_pagina):
            if i not in [pagina for paginas in self.tabla_paginas.values() for pagina in paginas]:
                return i
        return None
    
    def liberar_pagina(self, pagina):
        for proceso_id, paginas in self.tabla_paginas.items():
            if pagina in paginas:
                paginas.remove(pagina)
                if not paginas:
                    del self.tabla_paginas[proceso_id]
                break
    
    def liberar_memoria(self, proceso):
        self.memoria_disponible += proceso.tamanio
        for pagina in proceso.paginas:
            self.liberar_pagina(pagina)
        proceso.paginas = []
    
    def ejecutar_simulacion(self):
        while True:
            self.crear_proceso()
            
            # Intentar mover procesos de la cola de nuevos a la cola de listos
            for proceso in self.cola_nuevos[:]:
                if self.asignar_memoria(proceso):
                    proceso.estado = "Listo"
                    self.cola_nuevos.remove(proceso)
                    self.cola_listos.append(proceso)
            
            # Ejecutar proceso
            if self.proceso_ejecutando is None and self.cola_listos:
                self.proceso_ejecutando = self.cola_listos.pop(0)
                self.proceso_ejecutando.estado = "Ejecutando"
                
                # Simular uso de recurso compartido
                with self.recurso_compartido:
                    time.sleep(random.uniform(0.5, 2))
                
                self.proceso_ejecutando.estado = "Terminado"
                self.liberar_memoria(self.proceso_ejecutando)
                self.proceso_ejecutando = None
            
            self.actualizar_ui()
            time.sleep(0.1)
    
    def actualizar_ui(self):
        # Actualizar la interfaz gráfica aquí...
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorProcesos(root)
    root.mainloop()
