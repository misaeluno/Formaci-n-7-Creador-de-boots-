# fix_dependencies.py
import subprocess
import sys

def run_command(command):
    """Ejecuta un comando y muestra el resultado"""
    print(f"Ejecutando: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.stdout:
        print("Salida:", result.stdout)
    if result.stderr:
        print("Errores:", result.stderr)
    return result.returncode == 0

def main():
    print("=" * 60)
    print("SOLUCIONADOR DE DEPENDENCIAS PARA ROBOT ACME")
    print("=" * 60)
    
    print("\n1. Desinstalando versiones conflictivas...")
    run_command("pip uninstall pandas numpy selenium openpyxl keyring -y")
    
    print("\n2. Instalando versiones compatibles...")
    
    # Versiones compatibles probadas
    packages = [
        "numpy==1.26.4",
        "pandas==2.1.4", 
        "selenium==4.15.0",
        "openpyxl==3.1.0",
        "keyring==24.0.0"
    ]
    
    all_success = True
    for package in packages:
        success = run_command(f"pip install {package}")
        if not success:
            all_success = False
    
    print("\n3. Verificando instalacion...")
    
    test_code = """
try:
    import numpy, pandas, selenium, openpyxl, keyring
    print("NumPy:", numpy.__version__)
    print("Pandas:", pandas.__version__)
    print("Selenium:", selenium.__version__)
    print("Openpyxl:", openpyxl.__version__)
    print("Keyring:", keyring.__version__)
    print("\\n¡Todas las dependencias instaladas correctamente!")
except Exception as e:
    print("Error:", str(e))
"""
    
    result = subprocess.run([sys.executable, "-c", test_code], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Errores:", result.stderr)
    
    print("=" * 60)
    if all_success and "Error" not in result.stdout:
        print("SOLUCION COMPLETADA EXITOSAMENTE")
    else:
        print("HUBO PROBLEMAS DURANTE LA SOLUCION")
    print("=" * 60)

if __name__ == "__main__":
    main()