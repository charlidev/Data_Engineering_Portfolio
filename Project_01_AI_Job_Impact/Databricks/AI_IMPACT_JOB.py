# Databricks notebook source
# DBTITLE 1,IMPORT LIBRARIES
from pyspark.sql import functions as F
from pyspark.sql.types import *

# COMMAND ----------

# DBTITLE 1,BRONZE LAYER
# Definiendo la ruta del archivo
file_path = "/Volumes/portfolio/default/raw_data_uploads/ai_job_impact.csv"

# Leyendo el CSV
df_bronze = (spark.read
             .format("csv")
             .option("header", "true")
             .option("inferSchema", "false")
             .load(file_path)
            )

# Guardando la tabla Bronze en formato Delta
df_bronze.write.format("delta").mode("overwrite").saveAsTable("portfolio.bronze.raw_ai_job_impact")

# Verificando la carga
print(f"Capa Bronze completada. Registros cargados: {df_bronze.count()}")
display(df_bronze.limit(5))

# COMMAND ----------

# DBTITLE 1,Silver Layer
# Cargando la tabla desde la capa Bronze
df_bronze = spark.read.table("portfolio.bronze.raw_ai_job_impact")

# Aplicacndo las transformaciones
df_silver = df_bronze.select(
    F.trim(F.col("Employee_ID")).alias("Employee_ID"),
    F.col("Age").cast("int").alias("Age"),
    F.trim(F.col("Gender")).alias("Gender"),
    F.trim(F.col("Education_Level")).alias("Education_Level"),
    F.trim(F.col("Industry")).alias("Industry"),
    F.trim(F.col("Job_Role")).alias("Job_Role"),
    F.col("Years_Experience").cast("int").alias("Years_Experience"),
    F.trim(F.col("AI_Adoption_Level")).alias("AI_Adoption_Level"),
    F.trim(F.col("Automation_Risk")).alias("Automation_Risk"),
    # Transformando los valores yes/no a booleanos
    F.when(F.upper(F.trim(F.col("Upskilling_Required"))) == "YES", True)
           .otherwise(False).alias("Upskilling_Required_Bool"),
    F.col("Salary_Before_AI").cast("decimal(10,2)").alias("Salary_Before_AI"),
    F.col("Salary_After_AI").cast("decimal(10,2)").alias("Salary_After_AI"),
    F.trim(F.col("Job_Status")).alias("Job_Status"),
    F.col("Work_Hours_Per_Week").cast("int").alias("Work_Hours_Per_Week"),
    F.when(F.upper(F.trim(F.col("Remote_Work"))) == "YES", True)
     .otherwise(False).alias("Remote_Work_Bool"),
    F.col("Job_Satisfaction").cast("int").alias("Job_Satisfaction"),
    F.col("Productivity_Change_%").cast("float").alias("Productivity_Change_Pct"),
    # Metadata para saber cuándo se procesó el dato
    F.current_timestamp().alias("Load_Timestamp")
)

# Guardando la tabla Silver en formato Delta
df_silver.write.format("delta").mode("overwrite").saveAsTable("portfolio.silver.ai_job_impact_silver")

# Imprimiendo resultados de la capa bronze
print("Capa silver completada con éxito.")
display(df_silver.limit(5))

# COMMAND ----------

# DBTITLE 1,Capa Gold
# Cargando los datos desde la capa Silver
df_silver = spark.read.table("portfolio.silver.ai_job_impact_silver")

# Insight #1 Impacto salarial por industria 
gold_salary = (df_silver.groupBy("Industry")
               .agg(
                   F.round(F.avg("Salary_Before_AI"), 2).alias("Avg_Salary_Pre_AI"),
                   F.round(F.avg("Salary_After_AI"), 2).alias("Avg_Salary_Post_AI")
               )
               .withColumn("Net_Change", F.round(F.col("Avg_Salary_Post_AI") - F.col("Avg_Salary_Pre_AI"), 2))
               .sort(F.col("Net_Change").desc())
               )

# Guardando como tabla delta gold
gold_salary.write.format("delta").mode("overwrite").saveAsTable("portfolio.gold.salary_impact")

# Insight #2 Riesgo de automatización vs Educacion
gold_risk = (df_silver.groupBy("Education_Level", "Automation_Risk")
            .agg(F.count("Employee_ID").alias("Employee_Count"))
            .sort("Education_Level", F.col("Employee_Count").desc()))

# Guardando como tabla delta gold
gold_risk.write.format("delta").mode("overwrite").saveAsTable("portfolio.gold.risk")

# Insight #3 Productividad vs Satisfaccion por rol
gold_performance = (df_silver.groupBy("Job_Role")
                    .agg(F.round(F.avg("Productivity_Change_Pct"), 2).alias("Avg_Prod_Gain"),
                         F.round(F.avg("Job_Satisfaction"), 2).alias("Avg_Satisfaction"))
                    .sort(F.col("Avg_Prod_Gain").desc()))

# Guardando la tabla Gold en formato Delta
gold_performance.write.format("delta").mode("overwrite").saveAsTable("portfolio.gold.performance_metrics")
print("Capa Gold completada.")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Borrar las tablas una por una para limpiar el esquema default
# MAGIC DROP TABLE IF EXISTS portfolio.default.ai_job_impact;
# MAGIC DROP TABLE IF EXISTS portfolio.default.ai_job_impact_silver;
# MAGIC DROP TABLE IF EXISTS portfolio.default.gold_performance_metrics;
# MAGIC DROP TABLE IF EXISTS portfolio.default.gold_risk;
# MAGIC DROP TABLE IF EXISTS portfolio.default.gold_salary_impact;
# MAGIC DROP TABLE IF EXISTS portfolio.default.old_performance_metrics;
# MAGIC DROP TABLE IF EXISTS portfolio.default.raw_ai_job_impact;