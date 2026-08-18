/* =====================================================================
   FINSIGHT — PHASE 9: SNOWFLAKE WAREHOUSE
   01_setup.sql

   PURPOSE
   -------
   Creates the foundational objects for the FinSight Snowflake warehouse:

     - Database
     - Warehouse (compute)
     - Four schemas:
         RAW -> STAGING -> CORE -> MART
     - Shared CSV file format
     - Internal stages for the three source CSV files

   ARCHITECTURAL NOTE
   ------------------
   FinSight currently has source CSV files on local disk and no cloud
   storage integration. Therefore, internal Snowflake stages are used.

   Local files will be uploaded with PUT and loaded with COPY INTO.

   If FinSight later moves to S3/Azure/GCS, the staging mechanism can be
   changed without redesigning the downstream STAGING/CORE/MART layers.

   IDEMPOTENCY
   -----------
   Objects are created with CREATE IF NOT EXISTS / CREATE OR REPLACE
   wherever appropriate so this setup can be safely re-run.
   ===================================================================== */


-- =====================================================================
-- 1. WAREHOUSE
-- =====================================================================

CREATE WAREHOUSE IF NOT EXISTS FINSIGHT_WH
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Compute for FinSight Phase 9 Snowflake warehouse.';

USE WAREHOUSE FINSIGHT_WH;


-- =====================================================================
-- 2. DATABASE
-- =====================================================================

CREATE DATABASE IF NOT EXISTS FINSIGHT
    COMMENT = 'FinSight financial data engineering platform — Phase 9 Snowflake warehouse.';

USE DATABASE FINSIGHT;


-- =====================================================================
-- 3. SCHEMAS
-- =====================================================================

CREATE SCHEMA IF NOT EXISTS RAW
    COMMENT = 'Landing zone for source CSV data.';

CREATE SCHEMA IF NOT EXISTS STAGING
    COMMENT = 'Typed, cleaned and deduplicated source data.';

CREATE SCHEMA IF NOT EXISTS CORE
    COMMENT = 'Conformed star schema and business metrics.';

CREATE SCHEMA IF NOT EXISTS MART
    COMMENT = 'BI-ready analytical tables.';


-- =====================================================================
-- 4. SHARED CSV FILE FORMAT
-- =====================================================================

CREATE OR REPLACE FILE FORMAT RAW.FF_CSV_STANDARD
    TYPE = 'CSV'
    FIELD_DELIMITER = ','
    SKIP_HEADER = 1
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    NULL_IF = ('', 'NULL', 'null', 'NaN', 'N/A')
    EMPTY_FIELD_AS_NULL = TRUE
    TRIM_SPACE = TRUE
    ERROR_ON_COLUMN_COUNT_MISMATCH = TRUE
    COMMENT = 'Standard CSV format for FinSight source files.';


-- =====================================================================
-- 5. INTERNAL STAGES
-- =====================================================================

CREATE STAGE IF NOT EXISTS RAW.STG_INDUSTRIES
    FILE_FORMAT = RAW.FF_CSV_STANDARD
    COMMENT = 'Internal stage for industries.csv';

CREATE STAGE IF NOT EXISTS RAW.STG_COMPANIES
    FILE_FORMAT = RAW.FF_CSV_STANDARD
    COMMENT = 'Internal stage for companies.csv';

CREATE STAGE IF NOT EXISTS RAW.STG_FINANCIALS
    FILE_FORMAT = RAW.FF_CSV_STANDARD
    COMMENT = 'Internal stage for financials.csv';


-- =====================================================================
-- 6. VERIFICATION
-- =====================================================================

SHOW WAREHOUSES LIKE 'FINSIGHT_WH';

SHOW DATABASES LIKE 'FINSIGHT';

SHOW SCHEMAS IN DATABASE FINSIGHT;

SHOW FILE FORMATS IN SCHEMA FINSIGHT.RAW;

SHOW STAGES IN SCHEMA FINSIGHT.RAW;