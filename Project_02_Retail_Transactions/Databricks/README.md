# Proyecto de Ingeniería de Datos: Retail Transactions (Databricks Edition)

Este proyecto implementa un pipeline de datos robusto utilizando la **Arquitectura Medallón** (Bronze, Silver, Gold) en **Databricks** con **PySpark**. El objetivo es procesar un conjunto de datos de transacciones de retail para generar insights estratégicos de negocio listos para su consumo en herramientas de BI como Power BI.

## 🏗️ Arquitectura del Proyecto

El pipeline sigue el flujo de procesamiento de datos escalable:

1.  **Capa Bronze (Raw):** Ingesta de datos crudos desde archivos CSV alojados en Volumes de Unity Catalog. Se enfoca en la preservación de la fidelidad de los datos y el manejo de esquemas iniciales (limpieza de caracteres especiales en encabezados).
2.  **Capa Silver (Cleansed):** Refinamiento y normalización. Incluye casteo de tipos de datos, limpieza de strings, normalización de formatos de fecha y extracción de metadatos (como el estado de la tienda mediante expresiones regulares).
3.  **Capa Gold (Curated):** Tablas Delta optimizadas para analítica de negocio. Contiene agregaciones y KPIs clave para la toma de decisiones.

## 🛠️ Tecnologías Utilizadas

* **Plataforma:** Databricks (Unity Catalog).
* **Motor de Procesamiento:** PySpark (Spark SQL).
* **Formato de Almacenamiento:** Delta Lake.
* **Lenguajes:** Python, SQL.

## 📋 Estructura de las Capas

### 🥉 Capa Bronze
* **Fuente:** `Retail_Transaction_Dataset.csv`
* **Proceso:** Ingesta mediante `DataFrameReader` con manejo de delimitadores y comillas opcionales (`quote`).
* **Desafío resuelto:** Limpieza de nombres de columnas con caracteres ilegales (ej. `%`, `()`) para asegurar compatibilidad con el almacenamiento Delta.

### 🥈 Capa Silver
* **Transformaciones:**
    * Casteo de tipos (`IntegerType`, `FloatType`).
    * Normalización de timestamps con patrones flexibles (`M/d/yyyy H:mm`).
    * Extracción de `STORE_STATE` mediante `regexp_extract` sobre la columna de ubicación.
    * Filtrado de registros nulos en campos críticos.

### 🥇 Capa Gold (Insights)
Generación de 7 vistas/tablas de negocio:
1.  **Rentabilidad por Categoría:** Ingresos totales y descuentos promedio.
2.  **Rendimiento Geográfico:** Ventas por estado.
3.  **Tendencia Temporal:** Análisis de ingresos mensuales.
4.  **Método de Pago:** Valor de ticket promedio por método.
5.  **Efectividad del Descuento:** Distribución de unidades vendidas por rangos de descuento.
6.  **Ranking de Productos:** Top 10 productos "Best-Sellers".
7.  **Canasta Promedio:** Tamaño promedio de cesta por categoría.

## 🚀 Hoja de Ruta hacia Producción (Next Steps)

Para escalar este proyecto a un entorno productivo real, se contemplan las siguientes mejoras:

* **Ingesta Automatizada:** Integración con **AWS S3** y **Auto Loader** para ingesta basada en eventos.
* **Generación de Datos:** Uso de scripts de Python con la librería `Faker` para simular el crecimiento continuo del dataset.
* **Orquestación:** Implementación de **Databricks Workflows** o **Azure Data Factory** para encadenar las ejecuciones.
* **Gobernanza:** Configuración de roles (RBAC) en Unity Catalog siguiendo el principio de menor privilegio.
* **CI/CD:** Automatización de despliegues mediante **GitHub Actions**.

---
*Proyecto desarrollado por Carlos Daniel Martínez López*
