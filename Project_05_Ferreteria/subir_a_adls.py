import os
import shutil
from dotenv import load_dotenv
from azure.storage.filedatalake import DataLakeServiceClient

# Cargar las variables de entorno
load_dotenv()

CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")

# Definir las rutas de origen base y la ruta de archivo (procesados)
CATALOGOS_DIR = os.getenv("CATALOGOS_DIR", "data/datos_bronce/catalogos")
TRANSACCIONES_DIR = os.getenv("TRANSACCIONES_DIR", "data/datos_bronce/transacciones")
ARCHIVE_DIR = os.getenv("ARCHIVE_DIR", "data/datos_bronce/procesados")

def subir_directorio_a_adls(file_system_client, base_local_dir, prefijo_nube, mover_a_procesados=True):
    """
    Recorre un directorio local y sube los CSV a ADLS. 
    Si mover_a_procesados es True, archiva los archivos locales tras subirlos.
    """
    ruta_absoluta = os.path.abspath(base_local_dir)
    ruta_archive_base = os.path.abspath(ARCHIVE_DIR)
    
    if not os.path.exists(ruta_absoluta):
        print(f"Advertencia: No se encontró la carpeta local {ruta_absoluta}")
        return

    # os.walk recorre la carpeta base y todas sus subcarpetas
    for root, _, files in os.walk(ruta_absoluta):
        # Filtrar solo archivos CSV
        archivos_csv = [f for f in files if f.endswith('.csv')]
        
        for file_name in archivos_csv:
            # 1. Rutas de origen
            local_file_path = os.path.join(root, file_name)
            
            # 2. Rutas para la nube
            ruta_relativa = os.path.relpath(local_file_path, ruta_absoluta)
            ruta_relativa_nube = ruta_relativa.replace("\\", "/")
            ruta_destino_nube = f"{prefijo_nube}/{ruta_relativa_nube}"
            
            # 3. Subir el archivo a Azure
            file_client = file_system_client.get_file_client(ruta_destino_nube)
            with open(local_file_path, "rb") as datos_archivo:
                print(f"Subiendo -> {CONTAINER_NAME}/{ruta_destino_nube}")
                file_client.upload_data(datos_archivo, overwrite=True)
            
            # 4. Lógica de archivado condicional
            if mover_a_procesados:
                ruta_archive_final = os.path.join(ruta_archive_base, prefijo_nube, ruta_relativa)
                os.makedirs(os.path.dirname(ruta_archive_final), exist_ok=True)
                shutil.move(local_file_path, ruta_archive_final)
                print(f"  └─ Movido a archivo local: {ruta_archive_final}")
            else:
                print(f"  └─ Mantenido en carpeta de origen (Modo Catálogo)")

def main():
    try:
        print("Conectando con Azure Data Lake Storage Gen2...")
        service_client = DataLakeServiceClient.from_connection_string(CONNECTION_STRING)
        file_system_client = service_client.get_file_system_client(file_system=CONTAINER_NAME)
        
        print("\n=== Sincronizando Catálogos Maestros ===")
        # Le pasamos False para que NO mueva los catálogos
        subir_directorio_a_adls(file_system_client, CATALOGOS_DIR, "catalogos", mover_a_procesados=False)
        
        print("\n=== Sincronizando Transacciones Diarias ===")
        # Le pasamos True (o lo dejamos vacío ya que es el valor por defecto) para limpiar las transacciones
        subir_directorio_a_adls(file_system_client, TRANSACCIONES_DIR, "transacciones", mover_a_procesados=True)
        
        print("\n¡Sincronización completada! Tu Data Lake está al día.")

    except Exception as e:
        print(f"Error crítico durante la subida: {e}")

if __name__ == "__main__":
    main()