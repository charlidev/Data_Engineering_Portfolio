# Importar el módulo 'os' para interactuar con el sistema operativo y leer variables de entorno
import os
# Importar 'csv' para leer y escribir archivos en formato de valores separados por comas sin usar librerías pesadas
import csv
# Importar 'random' para generar números aleatorios y aplicar probabilidades a la generación de "datos sucios"
import random
# Importar 'load_dotenv' para cargar las variables definidas en el archivo oculto .env al entorno de ejecución
from dotenv import load_dotenv
# Importar 'Faker' para generar datos sintéticos realistas (nombres, RFCs, fechas, etc.)
from faker import Faker

# Ejecutar la función load_dotenv() para que las variables del archivo .env estén disponibles en os.environ
load_dotenv()

# Obtener la ruta de salida desde las variables de entorno; si no existe, usar './salida' por defecto
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./salida")
# Obtener el número de clientes desde las variables de entorno; convertirlo a entero (por defecto 100)
NUM_CLIENTES = int(os.getenv("NUM_CLIENTES_SINTETICOS", 100))

# Inicializar la instancia de Faker configurada para generar datos con el formato y cultura de México
fake = Faker('es_MX')
# Establecer una semilla fija (seed) para Faker y random, garantizando que el script genere los mismos datos cada vez que se ejecute
Faker.seed(42)
random.seed(42)

def inicializar_directorios():
    # Comprobar si el directorio de salida especificado NO existe en el sistema
    if not os.path.exists(OUTPUT_DIR):
        # Crear el directorio y cualquier directorio padre necesario si no existen
        os.makedirs(OUTPUT_DIR)

def generar_productos():
    # Definir la lista de diccionarios con la data base de los productos de la ferretería
    productos = [
        {"id_producto": 101, "sku": "BROC-01", "descripcion": "Broca Forstner 20mm", "id_subcategoria": 10, "id_proveedor": 1,"marca": "Truper", "precio_venta": 150.00, "precio_compra": 100.00},
        {"id_producto": 102, "sku": "DISC-01", "descripcion": "Disco TCG 100 dientes", "id_subcategoria": 11, "id_proveedor": 2, "marca": "Truper", "precio_venta": 700.00, "precio_compra": 550.00},
        {"id_producto": 103, "sku": "MOT-01", "descripcion": "Motor 2 HP", "id_subcategoria": 12, "id_proveedor": 3, "marca": "WEG", "precio_venta": 3000.00, "precio_compra": 2500.00},
        {"id_producto": 104, "sku": "MDF-18", "descripcion": "Hoja MDF 18mm 122x244", "id_subcategoria": 13, "id_proveedor": 4, "marca": "Arauco", "precio_venta": 650.00, "precio_compra": 590.00},
        # Dato sucio: Marca vacía (simulando un olvido en la captura del sistema origen)
        {"id_producto": 105, "sku": "PERF-01", "descripcion": "Perfil Gola Aluminio", "id_subcategoria": 14, "id_proveedor": 5, "marca": "", "precio_venta": "99", "precio_compra": 50.00},
        # Dato sucio: Registro duplicado intencional con minúsculas y espacios extra (simulando captura manual errónea)
        {"id_producto": 106, "sku": "BROC-01 ", "descripcion": "broca forstner 20mm ", "id_subcategoria": 15, "id_proveedor": 6, "marca": "truper", "precio_venta": 150.00, "precio_compra": 100.00}
    ]
    # Retornar la lista de productos generada|
    return productos

def generar_clientes(cantidad):
    # Inicializar una lista vacía que almacenará los registros de clientes
    clientes = []
    # Iniciar un bucle que iterará la cantidad de veces especificada por el parámetro 'cantidad'
    for i in range(1, cantidad + 1):
        # Generar un nombre completo realista usando Faker
        nombre = fake.name()
        
        # Inyectar suciedad: 20% de probabilidad de convertir el nombre a minúsculas o mezclar símbolos
        if random.random() < 0.20:
            # Sobrescribir el nombre a minúsculas simulando mala captura
            nombre = nombre.lower()
        # Inyectar suciedad: 5% de probabilidad de agregar caracteres especiales accidentalmente
        elif random.random() < 0.05:
            # Concatenar un símbolo extraño al final del nombre
            nombre = nombre + " _*"
            
        # Generar un RFC válido según el formato mexicano usando Faker
        rfc = fake.rfc()
        # Inyectar suciedad: 15% de probabilidad de dejar el RFC vacío (nulo)
        if random.random() < 0.15:
            # Asignar una cadena vacía en lugar del RFC generado
            rfc = ""
            
        # Crear un diccionario con la estructura del cliente y agregarlo a la lista de clientes
        clientes.append({
            "id_cliente": i,
            "nombre": nombre,
            "rfc": rfc,
            # Generar una fecha de registro aleatoria dentro de la década actual, convirtiéndola a string
            "fecha_registro": str(fake.date_this_decade())
        })
    # Retornar la lista completa de clientes procesados
    return clientes

def guardar_csv(nombre_archivo, datos, campos):
    # Construir la ruta completa del archivo uniendo el directorio de salida y el nombre del archivo
    ruta_completa = os.path.join(OUTPUT_DIR, nombre_archivo)
    # Abrir el archivo en modo escritura ('w'), asegurando que la codificación sea UTF-8 y sin líneas en blanco extra (newline='')
    with open(ruta_completa, 'w', newline='', encoding='utf-8') as archivo:
        # Crear un objeto DictWriter de la librería csv, pasándole el archivo y la lista de nombres de columnas
        escritor = csv.DictWriter(archivo, fieldnames=campos)
        # Escribir la primera fila del archivo CSV, que contiene los nombres de las columnas (encabezados)
        escritor.writeheader()
        # Iterar sobre cada diccionario en la lista de 'datos' y escribir sus valores como una fila en el CSV
        escritor.writerows(datos)
    # Imprimir en consola un mensaje de éxito indicando dónde se guardó el archivo
    print(f"Archivo guardado exitosamente: {ruta_completa}")

def generar_categorias_subcategorias():
    # Definir la lista de categorías principales de la ferretería
    categorias = [
        {"id_categoria": 1, "nombre": "Herramienta de Corte", "estatus": "Activo"},
        {"id_categoria": 2, "nombre": "Sistemas Eléctricos", "estatus": "Activo"},
        {"id_categoria": 3, "nombre": "Maderas y Tableros", "estatus": "Activo"},
        {"id_categoria": 4, "nombre": "Herrajes y Ensambles", "estatus": "Activo"},
        # Dato sucio: Categoría inactiva con espacios extra
        {"id_categoria": 5, "nombre": "  Materiales Generales  ", "estatus": "inactivo"}
    ]
    
    # Definir las subcategorías vinculadas a las categorías principales mediante id_categoria
    subcategorias = [
        {"id_subcategoria": 10, "id_categoria": 1, "nombre": "Brocas"},
        {"id_subcategoria": 11, "id_categoria": 1, "nombre": "Discos de Sierra"},
        {"id_subcategoria": 12, "id_categoria": 2, "nombre": "Motores y Componentes"},
        {"id_subcategoria": 13, "id_categoria": 3, "nombre": "MDF y Melaminas"},
        {"id_subcategoria": 14, "id_categoria": 3, "nombre": "Enchapados"},
        {"id_subcategoria": 15, "id_categoria": 4, "nombre": "Perfiles y Tiradores"}
    ]
    # Retornar ambas listas como una tupla para desempaquetarlas al guardar
    return categorias, subcategorias

def generar_proveedores():
    # Definir un catálogo estático de proveedores reales y sintéticos
    proveedores = [
        {"id_proveedor": 1, "razon_social": "Truper S.A. de C.V.", "rfc": fake.rfc(), "dias_credito": 30},
        {"id_proveedor": 2, "razon_social": "WEG Equipos Eléctricos", "rfc": fake.rfc(), "dias_credito": 45},
        {"id_proveedor": 3, "razon_social": "Arauco Distribución", "rfc": fake.rfc(), "dias_credito": 60},
        {"id_proveedor": 4, "razon_social": "Bosch Herramientas", "rfc": fake.rfc(), "dias_credito": 30},
        # Dato sucio: Razón social en minúsculas y RFC faltante (nulo)
        {"id_proveedor": 5, "razon_social": "distribuidora local s.a.", "rfc": "", "dias_credito": 0}
    ]
    # Retornar la lista de proveedores
    return proveedores

def generar_sucursales():
    # Definir las ubicaciones físicas de la ferretería para futuros análisis geográficos y de inventario
    sucursales = [
        {"id_sucursal": 1, "nombre": "Matriz Emiliano Zapata", "m2_almacen": 1200, "activa": True},
        {"id_sucursal": 2, "nombre": "Sucursal Centro", "m2_almacen": 450, "activa": True},
        # Dato sucio: Sucursal registrada pero inactiva, simulando un cierre temporal o error en el sistema
        {"id_sucursal": 3, "nombre": "Bodega Norte ", "m2_almacen": 800, "activa": False}
    ]
    # Retornar la lista de sucursales
    return sucursales

def generar_empleados(cantidad, sucursales_ids):
    # Inicializar la lista vacía para almacenar los registros de empleados
    empleados = []
    # Definir los roles posibles dentro de la operación de la ferretería
    roles = ['Cajero', 'Almacenista', 'Asesor de Ventas', 'Gerente']
    
    # Iterar para crear la cantidad solicitada de empleados
    for i in range(1, cantidad + 1):
        # Generar nombre utilizando Faker
        nombre = fake.name()
        
        # Inyectar suciedad: 10% de probabilidad de capturar el nombre en minúsculas
        if random.random() < 0.10:
            nombre = nombre.lower()
            
        # Asignar un rol aleatorio de la lista definida
        rol = random.choice(roles)
        # Asignar aleatoriamente el empleado a una sucursal existente
        id_sucursal = random.choice(sucursales_ids)
        
        # Inyectar suciedad: 5% de probabilidad de que falte la fecha de contratación
        if random.random() < 0.05:
            fecha_contratacion = ""
        else:
            # Generar una fecha de contratación en la última década y convertirla a string
            fecha_contratacion = str(fake.date_between(start_date='-10y', end_date='today'))

        # Construir el diccionario del empleado y agregarlo a la lista
        empleados.append({
            "id_empleado": i,
            "nombre": nombre,
            "rol": rol,
            "id_sucursal": id_sucursal,
            "fecha_contratacion": fecha_contratacion
        })
    # Retornar la lista completa de empleados
    return empleados

# Bloque de ejecución principal: asegura que este código solo corra si el script se ejecuta directamente, no si se importa
# Bloque de ejecución principal
if __name__ == "__main__":
    # Asegurar que la carpeta de salida exista
    inicializar_directorios()
    
    print("Iniciando generación completa de catálogos maestros...")
    
    # --- 1. Generar Productos ---
    datos_productos = generar_productos()
    guardar_csv("productos.csv", datos_productos, datos_productos[0].keys())
    
    # --- 2. Generar Clientes ---
    datos_clientes = generar_clientes(NUM_CLIENTES)
    guardar_csv("clientes.csv", datos_clientes, datos_clientes[0].keys())
    
    # --- 3. Generar Categorías y Subcategorías ---
    # Desempaquetar la tupla devuelta por la función en dos variables separadas
    datos_cats, datos_subcats = generar_categorias_subcategorias()
    guardar_csv("categorias.csv", datos_cats, datos_cats[0].keys())
    guardar_csv("subcategorias.csv", datos_subcats, datos_subcats[0].keys())
    
    # --- 4. Generar Proveedores ---
    datos_proveedores = generar_proveedores()
    guardar_csv("proveedores.csv", datos_proveedores, datos_proveedores[0].keys())
    
    # --- 5. Generar Sucursales ---
    datos_sucursales = generar_sucursales()
    guardar_csv("sucursales.csv", datos_sucursales, datos_sucursales[0].keys())
    
    # --- 6. Generar Empleados ---
    # Extraer únicamente los IDs de las sucursales generadas mediante una list comprehension
    ids_sucursales = [s['id_sucursal'] for s in datos_sucursales]
    # Generar 20 empleados, distribuyéndolos en los IDs de las sucursales válidas
    datos_empleados = generar_empleados(20, ids_sucursales)
    guardar_csv("empleados.csv", datos_empleados, datos_empleados[0].keys())
    
    print("Generación de todos los catálogos completada exitosamente.")