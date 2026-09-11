import os
import csv
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from faker import Faker

# Cargar variables de entorno
load_dotenv()

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./salida")
NUM_ORDENES = int(os.getenv("NUM_ORDENES_VENTA", 200))

fake = Faker('es_MX')
Faker.seed(42)
random.seed(42)

# ==========================================
# FUNCIONES AUXILIARES (Lectura de Catálogos)
# ==========================================
def cargar_catalogo(nombre_archivo):
    """Lee un archivo CSV generado en la Fase 1 y lo devuelve como una lista de diccionarios."""
    ruta = os.path.join(OUTPUT_DIR, nombre_archivo)
    datos = []
    # Usamos try-except por si ejecutas este script sin haber corrido el de catálogos
    try:
        with open(ruta, 'r', encoding='utf-8') as archivo:
            lector = csv.DictReader(archivo)
            for fila in lector:
                datos.append(fila)
    except FileNotFoundError:
        print(f"Error: No se encontró {nombre_archivo}. Ejecuta primero el script de catálogos.")
        exit(1)
    return datos

def guardar_csv(nombre_archivo, datos, campos):
    """Guarda una lista de diccionarios en un archivo CSV."""
    ruta = os.path.join(OUTPUT_DIR, nombre_archivo)
    with open(ruta, 'w', newline='', encoding='utf-8') as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(datos)
    print(f"Archivo generado: {ruta}")

# ==========================================
# FUNCIONES DE GENERACIÓN DE TRANSACCIONES
# ==========================================
def generar_ventas_y_facturas(clientes, empleados, sucursales, productos, num_ordenes):
    ordenes_venta = []
    ordenes_detalle = []
    facturas = []
    
    # Filtrar solo sucursales activas y empleados con rol de ventas/caja
    sucursales_validas = [s['id_sucursal'] for s in sucursales if s['activa'] == 'True']
    
    id_detalle_global = 1
    
    for id_orden in range(1, num_ordenes + 1):
        # 1. Cabecera de la Orden
        id_cliente = random.choice(clientes)['id_cliente']
        id_sucursal = random.choice(sucursales_validas)
        # Filtramos empleados que pertenezcan a la sucursal de la venta
        empleados_sucursal = [e for e in empleados if e['id_sucursal'] == id_sucursal]
        id_empleado = random.choice(empleados_sucursal)['id_empleado'] if empleados_sucursal else random.choice(empleados)['id_empleado']
        
        # Simular una fecha de venta en los últimos 6 meses
        fecha_hora = fake.date_time_between(start_date='-6m', end_date='now')
        
        # Inyectar suciedad: 2% de probabilidad de que la fecha se registre vacía (falla del sistema)
        if random.random() < 0.02:
            fecha_str = ""
        else:
            fecha_str = fecha_hora.strftime("%Y-%m-%d %H:%M:%S")

        metodo_pago = random.choice(["Efectivo", "Tarjeta de Crédito", "Transferencia", "Tarjeta de Débito"])
        # Inyectar suciedad: Algunos tickets se quedan "Pendientes" o "Cancelados"
        estatus = random.choices(["Pagada", "Cancelada", "Pendiente"], weights=[90, 5, 5])[0]

        # 2. Detalles de la Orden (1 a 5 productos por ticket)
        num_productos_en_ticket = random.randint(1, 5)
        subtotal_orden = 0
        
        for _ in range(num_productos_en_ticket):
            producto = random.choice(productos)
            # Simulamos compra de materiales (ej. alguien llevándose varias hojas de MDF o perfiles)
            cantidad = random.randint(1, 15)
            precio_raw = producto.get('precio_venta', 0)
            try:
                precio_unit = float(precio_raw) if precio_raw not in ('', None) else 0.0
            except (TypeError, ValueError):
                precio_unit = 0.0
            
            # Inyectar suciedad: 1% de probabilidad de que se registre un descuento irreal o cantidad negativa
            descuento = 0.0
            if random.random() < 0.01:
                cantidad = -1  # Error de escaneo o devolución mal registrada
            elif random.random() < 0.05:
                descuento = precio_unit * 0.10 # 10% de descuento autorizado
                
            importe = (cantidad * precio_unit) - descuento
            subtotal_orden += importe if cantidad > 0 else 0
            
            ordenes_detalle.append({
                "id_detalle": id_detalle_global,
                "id_orden": id_orden,
                "id_producto": producto['id_producto'],
                "cantidad": cantidad,
                "precio_unitario_aplicado": round(precio_unit, 2),
                "descuento": round(descuento, 2)
            })
            id_detalle_global += 1

        # Calcular impuestos y total de la cabecera
        iva = subtotal_orden * 0.16
        total = subtotal_orden + iva
        
        ordenes_venta.append({
            "id_orden": id_orden,
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
        
        # 3. Facturación (No todos los tickets se facturan, solo ~40%)
        if estatus == "Pagada" and random.random() < 0.40:
            facturas.append({
                "id_factura": len(facturas) + 1,
                "id_orden": id_orden,
                "uuid": fake.uuid4(),
                "fecha_timbrado": (fecha_hora + timedelta(hours=random.randint(1, 4))).strftime("%Y-%m-%d %H:%M:%S")
            })

    return ordenes_venta, ordenes_detalle, facturas

def generar_movimientos_inventario(ordenes_detalle, ordenes_venta):
    """Genera el kardex de inventario basándose en las salidas de las ventas."""
    movimientos = []
    id_movimiento = 1
    
    # Crear un diccionario rápido para saber la fecha y sucursal de cada orden
    info_ordenes = { str(o['id_orden']): o for o in ordenes_venta }
    
    for detalle in ordenes_detalle:
        id_orden = str(detalle['id_orden'])
        if id_orden not in info_ordenes:
            continue
            
        orden = info_ordenes[id_orden]
        
        # Solo registrar salidas si la orden no está cancelada y la fecha existe
        if orden['estatus'] == 'Pagada' and orden['fecha_hora'] != "":
            # Inyectar suciedad: 5% de movimientos se registran como tipo "Ajuste" en lugar de "Salida"
            tipo_mov = "Salida" if random.random() > 0.05 else "Ajuste"
            
            movimientos.append({
                "id_movimiento": id_movimiento,
                "id_producto": detalle['id_producto'],
                "id_sucursal": orden['id_sucursal'],
                "tipo": tipo_mov,
                # Salida de inventario (negativo)
                "cantidad": -(int(detalle['cantidad'])), 
                "fecha_hora": orden['fecha_hora'],
                "id_orden_venta": id_orden,
                "id_orden_compra": ""
            })
            id_movimiento += 1
            
    return movimientos

# ==========================================
# BLOQUE PRINCIPAL
# ==========================================
if __name__ == "__main__":
    print("Cargando catálogos maestros desde CSV...")
    clientes = cargar_catalogo("clientes.csv")
    empleados = cargar_catalogo("empleados.csv")
    sucursales = cargar_catalogo("sucursales.csv")
    productos = cargar_catalogo("productos.csv")
    
    print(f"Generando {NUM_ORDENES} órdenes de venta y su facturación...")
    ventas, ventas_detalle, facturas = generar_ventas_y_facturas(clientes, empleados, sucursales, productos, NUM_ORDENES)
    
    print("Generando movimientos de inventario...")
    inventario = generar_movimientos_inventario(ventas_detalle, ventas)
    
    print("Guardando archivos de transacciones...")
    guardar_csv("ordenes_venta.csv", ventas, ventas[0].keys())
    guardar_csv("ordenes_venta_detalle.csv", ventas_detalle, ventas_detalle[0].keys())
    
    if facturas:
        guardar_csv("facturas.csv", facturas, facturas[0].keys())
    if inventario:
        guardar_csv("movimientos_inventario.csv", inventario, inventario[0].keys())
        
    print("¡Generación de Fase 2 completada! Los datos sucios han sido inyectados.")