from pyspark.sql import SparkSession


def create_spark_session() -> SparkSession:
    return (
        SparkSession.builder
        .appName("FinSightFinancialAnalytics")
        .master("local[*]")
        .getOrCreate()
    )