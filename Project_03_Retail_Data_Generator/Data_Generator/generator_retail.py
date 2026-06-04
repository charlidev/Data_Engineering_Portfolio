import os
import pandas as pd
import numpy as np
import boto3
import random
from datetime import datetime
from io import StringIO
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# === CONFIGURACIÓN ===
BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
REGION_NAME = os.getenv("AWS_REGION", "us-east-1")

# Validación de seguridad
if not all([AWS_ACCESS_KEY, AWS_SECRET_KEY, BUCKET_NAME]):
    raise ValueError("Error: Faltan credenciales en el archivo .env. Revisa AWS_ACCESS_KEY, AWS_SECRET_KEY y AWS_BUCKET_NAME.")

# Inicializar cliente de S3
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION_NAME
)

def upload_to_s3(df, entity_name):
    """
    Sube un DataFrame a S3 siguiendo la estructura de particionamiento Hive:
    landing/entidad/y=YYYY/m=MM/d=DD/archivo.csv
    """
    now = datetime.now()
    year, month, day = now.year, f"{now.month:02d}", f"{now.day:02d}"
    
    # Ruta profesional para Data Lake
    file_path = f"landing/{entity_name}/y={year}/m={month}/d={day}/{entity_name}_{now.strftime('%H%M%S')}.csv"
    
    # Convertir DF a buffer CSV
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    
    try:
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=file_path,
            Body=csv_buffer.getvalue()
        )
        print(f"✅ [S3] {entity_name} -> {file_path}")
    except Exception as e:
        print(f"❌ Error al subir {entity_name}: {e}")

def generate_full_retail_data():
    """Genera las 5 entidades principales del negocio"""
    print(f"🚀 Iniciando generación de datos para: {BUCKET_NAME}\n")
    
    # 1. Sucursales (Dimension)
    stores = pd.DataFrame({
        'store_id': [f"ST_{i:03d}" for i in range(1, 6)],
        'store_name': ['Norte', 'Sur', 'Centro', 'Este', 'Oeste'],
        'city': ['Pachuca', 'CDMX', 'Querétaro', 'Puebla', 'Toluca'],
        'store_type': ['Flagship', 'Standard', 'Express', 'Standard', 'Flagship']
    })
    upload_to_s3(stores, "dim_stores")

    # 2. Productos (Dimension)
    categories = ['Electrónica', 'Hogar', 'Herramientas', 'Ropa']
    products = pd.DataFrame({
        'sku': [f"PROD_{i:04d}" for i in range(1, 51)],
        'product_name': [f"Producto_{i}" for i in range(1, 51)],
        'category': [random.choice(categories) for _ in range(50)],
        'price': np.round(np.random.uniform(100, 5000, 50), 2)
    })
    upload_to_s3(products, "dim_products")

    # 3. Clientes (Dimension)
    clients = pd.DataFrame({
        'client_id': [f"CLI_{i:05d}" for i in range(1, 101)],
        'client_name': [f"User_{i}" for i in range(1, 101)],
        'email': [f"user{i}@example.com" for i in range(1, 101)],
        'segment': random.choices(['Gold', 'Silver', 'Bronze'], k=100)
    })
    upload_to_s3(clients, "dim_clients")

    # 4. Ventas (Fact - Transaccional)
    num_sales = 200
    sales = pd.DataFrame({
        'txn_id': [f"TXN_{i:06d}" for i in range(1, num_sales + 1)],
        'timestamp': [datetime.now().strftime('%Y-%m-%d %H:%M:%S') for _ in range(num_sales)],
        'client_id': [f"CLI_{random.randint(1, 100):05d}" for _ in range(num_sales)],
        'store_id': [f"ST_{random.randint(1, 5):03d}" for _ in range(num_sales)],
        'sku': [f"PROD_{random.randint(1, 50):04d}" for _ in range(num_sales)],
        'quantity': [random.randint(1, 5) for _ in range(num_sales)],
        'payment_method': random.choices(['Tarjeta', 'Efectivo', 'Transferencia'], k=num_sales)
    })
    # Calcular monto total basado en el precio del producto (simulación rápida)
    sales = sales.merge(products[['sku', 'price']], on='sku', how='left')
    sales['total_amount'] = sales['quantity'] * sales['price']
    upload_to_s3(sales.drop(columns=['price']), "fact_sales")

    # 5. Inventarios (Snapshot Diario)
    inventory = []
    for s_id in stores['store_id']:
        for p_sku in products['sku']:
            inventory.append({
                'snapshot_date': datetime.now().strftime('%Y-%m-%d'),
                'store_id': s_id,
                'sku': p_sku,
                'stock_level': random.randint(0, 150),
                'reorder_point': 20
            })
    upload_to_s3(pd.DataFrame(inventory), "fact_inventory")

    print("\n✨ Proceso terminado. Revisa tu bucket de S3.")

if __name__ == "__main__":
    generate_full_retail_data()