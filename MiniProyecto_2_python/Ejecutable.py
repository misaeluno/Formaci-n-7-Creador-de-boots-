# Ejecutable.py - Ejecuta todo el proceso automáticamente
import os
import sys
import subprocess
import time

def print_header(text):
    """Imprime un encabezado con formato"""
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)

def run_script(script_name, description):
    """Ejecuta un script de Python"""
    print_header(f"EJECUTANDO: {description}")
    
    if not os.path.exists(script_name):
        print(f"ERROR: No se encuentra el archivo {script_name}")
        return False
    
    try:
        # Ejecutar el script
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        # Mostrar salida
        if result.stdout:
            print(result.stdout)
        
        # Mostrar errores si los hay
        if result.stderr:
            print("ERRORES:", result.stderr)
        
        # Verificar si fue exitoso
        if result.returncode != 0:
            print(f"✗ {script_name} falló con código {result.returncode}")
            return False
        
        print(f"✓ {script_name} ejecutado exitosamente")
        return True
        
    except Exception as e:
        print(f"✗ Error ejecutando {script_name}: {e}")
        return False

def check_dependencies():
    """Verifica si las dependencias básicas están instaladas"""
    print_header("VERIFICANDO DEPENDENCIAS INICIALES")
    
    try:
        import pip
        print("✓ pip está instalado")
        return True
    except ImportError:
        print("✗ pip no está instalado")
        print("Instala pip primero: https://pip.pypa.io/en/stable/installation/")
        return False

def ask_credential_setup():
    """Pregunta al usuario si configuró las credenciales"""
    print_header("CONFIGURACIÓN DE CREDENCIALES WINDOWS")
    
    print("ANTES DE CONTINUAR, necesitas crear la credencial en Windows:")
    print("\n1. Abre PowerShell como Administrador")
    print("2. Ejecuta este comando (cambia TU_CONTRASEÑA):")
    print("   cmdkey /generic:MiniProyecto_2_Credencial /user:\"misael.gallardo.19@alumnos.uda.cl\" /pass:\"TU_CONTRASEÑA\"")
    print("\nO manualmente:")
    print("   - Panel de Control > Credenciales de Windows")
    print("   - Agregar credencial genérica")
    print("   - Nombre: MiniProyecto_2_Credencial")
    print("   - Usuario: misael.gallardo.19@alumnos.uda.cl")
    print("   - Contraseña: [tu contraseña]")
    
    response = input("\n¿Ya creaste la credencial en Windows? (s/n): ").strip().lower()
    return response == 's'

def create_fix_dependencies():
    """Crea el archivo fix_dependencies.py si no existe"""
    if not os.path.exists("fix_dependencies.py"):
        print("Creando fix_dependencies.py...")
        
        fix_content = '''# fix_dependencies.py
import subprocess
import sys

def main():
    print("=" * 60)
    print("SOLUCIONANDO PROBLEMAS DE DEPENDENCIAS")
    print("=" * 60)
    
    # Desinstalar versiones conflictivas
    print("\\n1. Desinstalando versiones conflictivas...")
    subprocess.run([sys.executable, "-m", "pip", "uninstall", "pandas", "numpy", "-y"])
    
    # Instalar versiones compatibles
    print("\\n2. Instalando versiones compatibles...")
    packages = [
        ("numpy", "1.26.4"),
        ("pandas", "2.1.4"),
        ("selenium", "4.15.0"),
        ("openpyxl", "3.1.0"),
        ("keyring", "24.0.0")
    ]
    
    for package, version in packages:
        print(f"  Instalando {package}=={version}...")
        subprocess.run([sys.executable, "-m", "pip", "install", f"{package}=={version}"])
    
    # Verificar
    print("\\n3. Verificando instalación...")
    subprocess.run([sys.executable, "-c", """
try:
    import numpy, pandas, selenium, openpyxl, keyring
    print("✓ NumPy:", numpy.__version__)
    print("✓ Pandas:", pandas.__version__)
    print("✓ Selenium:", selenium.__version__)
    print("✓ Openpyxl:", openpyxl.__version__)
    print("✓ Keyring:", keyring.__version__)
    print("\\n¡TODAS LAS DEPENDENCIAS INSTALADAS CORRECTAMENTE!")
except Exception as e:
    print("✗ Error:", e)
"""])
    
    print("\\n" + "=" * 60)
    print("PROCESO COMPLETADO")
    print("=" * 60)

if __name__ == "__main__":
    main()
'''
        
        with open("fix_dependencies.py", "w", encoding="utf-8") as f:
            f.write(fix_content)
        print("✓ fix_dependencies.py creado")

def create_config_simple():
    """Crea el archivo create_config_simple.py si no existe"""
    if not os.path.exists("create_config_simple.py"):
        print("Creando create_config_simple.py...")
        
        config_content = '''# create_config_simple.py
from openpyxl import Workbook

def main():
    print("=" * 60)
    print("CREANDO ARCHIVO DE CONFIGURACIÓN")
    print("=" * 60)
    
    # URL del sistema ACME
    acme_url = "https://acme-test.uipath.com/login"
    
    # Crear archivo Excel
    wb = Workbook()
    ws = wb.active
    
    # Encabezados
    ws['A1'] = 'acme_url'
    ws['B1'] = 'credential_asset'
    ws['C1'] = 'urgent_threshold'
    
    # Datos
    ws['A2'] = acme_url
    ws['B2'] = 'MiniProyecto_2_Credencial'
    ws['C2'] = 15
    
    # Guardar
    wb.save('config.xlsx')
    
    print(f"\\nconfig.xlsx creado con los siguientes valores:")
    print(f"  • URL ACME: {acme_url}")
    print(f"  • Nombre credencial: MiniProyecto_2_Credencial")
    print(f"  • Umbral días urgentes: 15")
    print("\\n¡ARCHIVO DE CONFIGURACIÓN CREADO EXITOSAMENTE!")
    print("=" * 60)

if __name__ == "__main__":
    main()
'''
        
        with open("create_config_simple.py", "w", encoding="utf-8") as f:
            f.write(config_content)
        print("✓ create_config_simple.py creado")

def update_main_apellido():
    """Actualiza el apellido en main.py si es necesario"""
    try:
        with open("main.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Buscar línea con "Gallardo" para cambiar
        if "Gallardo" in content:
            print("\n" + "=" * 60)
            print("ACTUALIZANDO APELLIDO EN main.py")
            print("=" * 60)
            
            print("En main.py se encuentra 'Gallardo' como apellido.")
            nuevo_apellido = input("Ingresa tu apellido real (o presiona Enter para mantener 'Gallardo'): ").strip()
            
            if nuevo_apellido:
                content = content.replace("Gallardo", nuevo_apellido)
                with open("main.py", "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"✓ Apellido cambiado a: {nuevo_apellido}")
            else:
                print("✓ Se mantiene 'Gallardo' como apellido")
    except:
        print("⚠ No se pudo verificar main.py")

def main():
    """Función principal que ejecuta todo en orden"""
    print_header("ROBOT AUDITOR ACME - EJECUCIÓN AUTOMÁTICA")
    print("Este script ejecutará todo el proceso en el orden correcto.")
    print("=" * 70)
    
    # Paso 0: Verificar dependencias básicas
    if not check_dependencies():
        print("No se pueden continuar sin pip instalado.")
        return
    
    # Paso 1: Crear scripts si no existen
    create_fix_dependencies()
    create_config_simple()
    
    # Paso 2: Preguntar por credenciales
    if not ask_credential_setup():
        print("\n⚠ Por favor crea la credencial en Windows primero.")
        print("El robot no podrá hacer login sin las credenciales.")
        continuar = input("\n¿Continuar de todas formas? (s/n): ").strip().lower()
        if continuar != 's':
            print("Proceso cancelado.")
            return
    
    # Paso 3: Actualizar apellido en main.py
    update_main_apellido()
    
    # Paso 4: Ejecutar fix_dependencies.py
    print("\n" + "=" * 70)
    print("INICIANDO PROCESO DE EJECUCIÓN")
    print("=" * 70)
    
    input("Presiona Enter para comenzar la instalación de dependencias...")
    
    if not run_script("fix_dependencies.py", "Solución de dependencias"):
        print("⚠ Hubo problemas con las dependencias. Continuando...")
    
    # Pequeña pausa
    time.sleep(2)
    
    # Paso 5: Ejecutar create_config_simple.py
    input("\nPresiona Enter para crear el archivo de configuración...")
    
    if not run_script("create_config_simple.py", "Creación de configuración"):
        print("✗ No se pudo crear la configuración. Abortando...")
        return
    
    # Paso 6: Ejecutar main.py
    print("\n" + "=" * 70)
    print("¡TODO LISTO PARA EJECUTAR EL ROBOT!")
    print("=" * 70)
    
    print("\nRESUMEN:")
    print("1. Dependencias instaladas ✓")
    print("2. Configuración creada ✓")
    print("3. Credenciales configuradas (verificar manualmente)")
    
    ejecutar = input("\n¿Ejecutar el robot ahora? (s/n): ").strip().lower()
    
    if ejecutar == 's':
        print("\nIniciando robot ACME...")
        print("=" * 70)
        run_script("main.py", "Robot Auditor ACME")
    else:
        print("\nPuedes ejecutar el robot manualmente con: python main.py")
    
    # Paso 7: Mostrar archivos generados
    print_header("ARCHIVOS GENERADOS")
    
    archivos = [
        ("config.xlsx", "Configuración del sistema"),
        ("Reporte_Prioridad_*.xlsx", "Reporte final (se generará después)"),
        ("*.png", "Screenshots para debugging")
    ]
    
    for archivo, descripcion in archivos:
        if archivo == "config.xlsx" and os.path.exists("config.xlsx"):
            print(f"✓ {archivo} - {descripcion}")
        else:
            print(f"  {archivo} - {descripcion}")
    
    print_header("PROCESO COMPLETADO")
    print("\nPara ejecutar solo el robot en el futuro:")
    print("  python main.py")
    print("\n¡Gracias por usar el Robot Auditor ACME!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProceso interrumpido por el usuario.")
    except Exception as e:
        print(f"\nError inesperado: {e}")
    input("\nPresiona Enter para salir...")