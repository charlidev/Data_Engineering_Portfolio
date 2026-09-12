import os
import csv
import random
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from faker import Faker

# Cargar variables de entorno
load_dotenv()

CATALOGOS_DIR = os.getenv("CATALOGOS_DIR", "data/datos_bronce/catalogos")
TRANSACCIONES_DIR = os.getenv("TRANSACCIONES_DIR", "data/datos_bronce/transacciones")
NUM_ORDENES = int(os.getenv("NUM_ORDENES_VENTA", 15))

fake = Faker('es_MX')

# Asegurar que la carpeta base de transacciones exista
os.makedirs(TRANSACCIONES_DIR, exist_ok=True)
# El archivo de estado vive en la raíz de transacciones, no en la carpeta diaria
ESTADO_FILE = os.path.join(TRANSACCIONES_DIR, "estado_incremental.json")

def cargar_estado():
    if os.path.exists(ESTADO_FILE):
        with open(ESTADO_FILE, 'r') as f:
            return json.load(f)
    return {
        "ultimo_id_orden": 0, 
        "ultimo_id_detalle": 0, 
        "ultimo_id_factura": 0, 
        "ultimo_id_movimiento": 0
    }

def guardar_estado(estado):
    with open(ESTADO_FILE, 'w') as f:
        json.dump(estado, f)

def cargar_catalogo(nombre_archivo):
    ruta = os.path.join(CATALOGOS_DIR, nombre_archivo)
    datos = []
    try:
        with open(ruta, 'r', encoding='utf-8') as archivo:
            lector = csv.DictReader(archivo)
            for fila in lector:
                datos.append(fila)
    except FileNotFoundError:
        print(f"Error: No se encontró {nombre_archivo}. Ejecuta primero el script de catálogos.")
        exit(1)
    return datos

def guardar_csv(ruta_completa, datos, campos):
    with open(ruta_completa, 'w', newline='', encoding='utf-8') as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(datos)
    print(f"Archivo generado: {ruta_completa}")

def generar_ventas_y_facturas(clientes, empleados, sucursales, productos, num_ordenes, estado):
    ordenes_venta = []
    ordenes_detalle = []
    facturas = []
    
    sucursales_validas = [s['id_sucursal'] for s in sucursales if s['activa'] == 'True']
    
    id_orden_actual = estado["ultimo_id_orden"]
    id_detalle_actual = estado["ultimo_id_detalle"]
    id_factura_actual = estado["ultimo_id_factura"]
    
    for _ in range(num_ordenes):
        id_orden_actual += 1
        id_cliente = random.choice(clientes)['id_cliente']
        id_sucursal = random.choice(sucursales_validas)
        empleados_sucursal = [e for e in empleados if e['id_sucursal'] == id_sucursal]
        id_empleado = random.choice(empleados_sucursal)['id_empleado'] if empleados_sucursal else random.choice(empleados)['id_empleado']
        
        fecha_hora = datetime.now() - timedelta(minutes=random.randint(1, 1440))
        
        if random.random() < 0.02:
            fecha_str = ""
        else:
            fecha_str = fecha_hora.strftime("%Y-%m-%d %H:%M:%S")

        metodo_pago = random.choice(["Efectivo", "Tarjeta de Crédito", "Transferencia", "Tarjeta de Débito"])
        estatus = random.choices(["Pagada", "Cancelada", "Pendiente"], weights=[90, 5, 5])[0]

        num_productos_en_ticket = random.randint(1, 5)
        subtotal_orden = 0
        
        for _ in range(num_productos_en_ticket):
            id_detalle_actual += 1
            producto = random.choice(productos)
            cantidad = random.randint(1, 15)
            
            precio_raw = producto.get('precio_venta', 0)
            try:
                precio_unit = float(precio_raw) if precio_raw not in ('', None) else 0.0
            except (TypeError, ValueError):
                precio_unit = 0.0
            
            descuento = 0.0
            if random.random() < 0.01:
                cantidad = -1 
            elif random.random() < 0.05:
                descuento = precio_unit * 0.10
                
            importe = (cantidad * precio_unit) - descuento
            subtotal_orden += importe if cantidad > 0 else 0
            
            ordenes_detalle.append({
                "id_detalle": id_detalle_actual,
                "id_orden": id_orden_actual,
                "id_producto": producto['id_producto'],
                "cantidad": cantidad,
                "precio_unitario_aplicado": round(precio_unit, 2),
                "descuento": round(descuento, 2)
            })

        iva = subtotal_orden * 0.16
        total = subtotal_orden + iva
        
        ordenes_venta.append({
            "id_orden": id_orden_actual,
            "id_cliente": id_cliente,
            "id_empleado": id_empleado,
            "id_sucursal": id_sucursal,
            "fecha_hora": fecha_str,
            "subtotal": round(subtotal_orden, 2),
            "iva": round(iva, 2),
            "total": round(total, 2),
            "metodo_pago": metodo_pago,
            "estatus": estatus
        })
        
        if estatus == "Pagada" and random.random() < 0.40:
            id_factura_actual += 1
            facturas.append({
                "id_factura": id_factura_actual,
                "id_orden": id_orden_actual,
                "uuid": fake.uuid4(),
                "fecha_timbrado": (fecha_hora + timedelta(hours=random.randint(1, 4))).strftime("%Y-%m-%d %H:%M:%S")
            })

    estado["ultimo_id_orden"] = id_orden_actual
    estado["ultimo_id_detalle"] = id_detalle_actual
    estado["ultimo_id_factura"] = id_factura_actual
    
    return ordenes_venta, ordenes_detalle, facturas, estado

def generar_movimientos_inventario(ordenes_detalle, ordenes_venta, estado):
    movimientos = []
    id_movimiento_actual = estado["ultimo_id_movimiento"]
    info_ordenes = { str(o['id_orden']): o for o in ordenes_venta }
    
    for detalle in ordenes_detalle:
        id_orden = str(detalle['id_orden'])
        if id_orden not in info_ordenes:
            continue
            
        orden = info_ordenes[id_orden]
        
        if orden['estatus'] == 'Pagada' and orden['fecha_hora'] != "":
            id_movimiento_actual += 1
            tipo_mov = "Salida" if random.random() > 0.05 else "Ajuste"
            
            movimientos.append({
                "id_movimiento": id_movimiento_actual,
                "id_producto": detalle['id_producto'],
                "id_sucursal": orden['id_sucursal'],
                "tipo": tipo_mov,
                "cantidad": -(int(detalle['cantidad'])), 
                "fecha_hora": orden['fecha_hora'],
                "id_orden_venta": id_orden,
                "id_orden_compra": ""
            })
            
    estado["ultimo_id_movimiento"] = id_movimiento_actual
    return movimientos, estado

if __name__ == "__main__":
    print("Cargando estado previo y catálogos...")
    estado_actual = cargar_estado()
    
    clientes = cargar_catalogo("clientes.csv")
    empleados = cargar_catalogo("empleados.csv")
    sucursales = cargar_catalogo("sucursales.csv")
    productos = cargar_catalogo("productos.csv")
    
    print(f"Generando {NUM_ORDENES} transacciones incrementales...")
    ventas, ventas_detalle, facturas, estado_actual = generar_ventas_y_facturas(clientes, empleados, sucursales, productos, NUM_ORDENES, estado_actual)
    
    inventario, estado_actual = generar_movimientos_inventario(ventas_detalle, ventas, estado_actual)
    
    # 1. Generar la carpeta del día actual
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    carpeta_dia = os.path.join(TRANSACCIONES_DIR, fecha_hoy)
    os.makedirs(carpeta_dia, exist_ok=True)
    
    # 2. Generar el timestamp para los archivos
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print(f"Guardando archivos de transacciones en: {carpeta_dia} ...")
    
    # 3. Guardar usando os.path.join para concatenar la ruta dinámica
    guardar_csv(os.path.join(carpeta_dia, f"ordenes_venta_{timestamp}.csv"), ventas, ventas[0].keys())
    guardar_csv(os.path.join(carpeta_dia, f"ordenes_venta_detalle_{timestamp}.csv"), ventas_detalle, ventas_detalle[0].keys())
    
    if facturas:
        guardar_csv(os.path.join(carpeta_dia, f"facturas_{timestamp}.csv"), facturas, facturas[0].keys())
    if inventario:
        guardar_csv(os.path.join(carpeta_dia, f"movimientos_inventario_{timestamp}.csv"), inventario, inventario[0].keys())
        
    guardar_estado(estado_actual)
    print("¡Lote incremental generado y organizado exitosamente!")