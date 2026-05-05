📊 Retail End-to-End Data Pipeline: Snowflake + Power BI
Este proyecto implementa una arquitectura de datos moderna (Medallion Architecture) para procesar y analizar 100,000 registros de transacciones retail. El objetivo es transformar datos crudos en insights estratégicos accionables utilizando Snowflake como Data Warehouse y Power BI para la capa de visualización.

🚀 Arquitectura del Proyecto
El pipeline sigue el flujo de procesamiento en capas dentro de Snowflake:

Capa Bronze (Raw): Ingesta de datos crudos desde archivos CSV.

Capa Silver (Cleaned): Limpieza de datos, manejo de nulos, tipado de fechas y normalización de monedas.

Capa Gold (Curated/Analytics): Creación de 8 vistas de negocio (Business Insights) listas para consumo analítico.

Capa de Visualización: Conexión vía Power BI para la creación de Dashboards interactivos.

🛠️ Stack Tecnológico
Data Warehouse: Snowflake (Enterprise Edition).

Lenguaje de Transformación: SQL (Snowflake Dialect).

Visualización: Power BI Desktop (Conector nativo de Snowflake).

Dataset: 100k registros de transacciones retail (Sintético).

💡 Key Insights Generados
Se desarrollaron 8 vistas estratégicas en la capa Gold:

Rentabilidad por Categoría: Cruce de ingresos vs. porcentajes de descuento.

Rendimiento Geográfico: Identificación de estados con mayor volumen de venta.

Segmentación de Clientes (RFM): Clasificación en categorías Premium, Regular y Low Value.

Tendencia Temporal: Análisis de picos de venta diarios y mensuales.

Métodos de Pago: Correlación entre el tipo de pago y el ticket promedio.

Efectividad del Descuento: Impacto real de las promociones en el volumen de unidades vendidas.

Top 10 Best-Sellers: Ranking de productos por ingresos.

Average Basket Size: KPI de eficiencia de ventas cruzadas.

📈 Resultados y Conclusiones Técnicas
Optimización: El uso de Views en Snowflake permitió una capa Gold ágil y siempre actualizada sin duplicar almacenamiento innecesario.

Descubrimiento de Negocio: Se detectó que los descuentos superiores al 15% no incrementan significativamente el volumen de ventas en este dataset, sugiriendo una oportunidad de optimización de márgenes.

🛠️ Cómo Replicar
Ejecutar los scripts de la carpeta /sql en tu instancia de Snowflake.

Configurar el Warehouse COMPUTE_WH y la Database RETAIL_TRANSACTIONS.

Conectar Power BI utilizando el Server URL de tu cuenta.

Importar las vistas de la capa GOLD.