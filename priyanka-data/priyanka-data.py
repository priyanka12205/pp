import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Paths
raw_path = "s3://rawbucketp/financial_data_updated.csv"
staging_path = "s3://stagingbucketp/financial_data_staging/"
curated_path = "s3://curatedbucketp/financial_data_curated/"

# Read from raw
df_raw = spark.read.option("header", True).option("inferSchema", True).csv(raw_path)

# ✅ Filter using valid column
df_staging = df_raw.filter(df_raw["Profit"].isNotNull())

# Write staging data
df_staging.write.mode("overwrite").parquet(staging_path)

# Lowercase columns
df_curated = df_staging.toDF(*[col.lower() for col in df_staging.columns])

# Write curated data
df_curated.write.mode("overwrite").parquet(curated_path)

job.commit()

