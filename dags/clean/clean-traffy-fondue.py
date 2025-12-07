import os
import sys

# ----------------------------------------------------------------------------------------------------
# 🔥 [ส่วนแก้ไขที่ 1] ตั้งค่า Environment (แก้ Path Java ให้ตรงกับเครื่องอ้วนนะครับ)
# ถ้าใช้ Java 17 ให้ชี้ไปที่โฟลเดอร์ Java 17 ของคุณ
# ตัวอย่าง: C:\Program Files\Eclipse Adoptium\jdk-17.0.13.11-hotspot
# ----------------------------------------------------------------------------------------------------
os.environ["JAVA_HOME"] = r"C:\Program Files\Eclipse Adoptium\jdk-17.0.17.10-hotspot"

# ตั้งค่า Hadoop Home (จำเป็นสำหรับ Spark บน Windows)
# ถ้ายังไม่มี winutils ให้ข้ามบรรทัดนี้ไปก่อน แต่ถ้ามี Error ตอนเซฟ ต้องกลับมาทำ
# os.environ["HADOOP_HOME"] = r"C:\hadoop" 
# ----------------------------------------------------------------------------------------------------

from functools import reduce
from pyspark.sql import SparkSession
from pyspark.sql.functions import (col, trim, lower, regexp_replace, sum, udf, to_timestamp, split, datediff, substring, length,
                                   current_timestamp, when, lit, year, try_to_timestamp, to_date, floor, row_number, min)
from pyspark.sql.types import ArrayType, StringType, StructType, StructField, IntegerType, FloatType
from pyspark.sql.window import Window

# เริ่มต้น Spark Session
spark = SparkSession.builder \
    .appName("TraffyFondueDataCleaning") \
    .config("spark.executor.memory", "4g") \
    .config("spark.driver.memory", "4g") \
    .getOrCreate()

sc = spark.sparkContext

# 🔥 [ส่วนแก้ไขที่ 2] ใช้ Absolute Path (Path เต็ม) และแก้ชื่อโฟลเดอร์เป็น 'traffy-fondue' (ขีดกลาง)
file_path = r"C:\Year_2\DSDE\dsdengdeng-project-dsde\data\raw\traffy-fondue\bangkok_2025-12.csv"

# ----------------------------------------------------------------------------------------------------

traffy_schema = StructType([
    StructField("ticket_id", StringType(), True),
    StructField("type", StringType(), True),         
    StructField("organization", StringType(), True), 
    StructField("comment", StringType(), True),      
    StructField("photo", StringType(), True),
    StructField("photo_after", StringType(), True),
    StructField("coords", StringType(), True),       
    StructField("address", StringType(), True),
    StructField("subdistrict", StringType(), True),
    StructField("district", StringType(), True),
    StructField("province", StringType(), True),
    StructField("timestamp", StringType(), True),    
    StructField("state", StringType(), True),        
    StructField("star", FloatType(), True),          
    StructField("count_reopen", IntegerType(), True), 
    StructField("last_activity", StringType(), True)  
])

print(f"กำลังอ่านไฟล์จาก: {file_path}")

# อ่านไฟล์ CSV
df_traffy = spark.read.csv(
    file_path,
    header=True,
    schema=traffy_schema,
    multiLine=True, 
    escape='"',
    encoding='UTF-8' # บังคับอ่านภาษาไทยให้ถูกต้อง
)

# ------------------------------------------------------------------
# Filter ประเภทปัญหา
livability_types = [
    "ถนน", "ทางเท้า", "ความปลอดภัย", "แสงสว่าง", "ความสะอาด",
    "กีดขวาง", "ท่อระบายน้ำ", "น้ำท่วม", "ต้นไม้", "PM2", "จราจร", "สะพาน"
]

df_filtered_type = df_traffy.filter(
    reduce(lambda a, b: a | b, [col("type").contains(t) for t in livability_types])
)

active_states = ["กำลังดำเนินการ", "รอรับเรื่อง"]
df_filtered_type = df_filtered_type.withColumn("state", trim(col("state")))
df_filtered_type = df_filtered_type.filter(col("state").isin(active_states))

# ------------------------------------------------------------------
# กรองพิกัดเฉพาะกรุงเทพฯ
df_final_spatial = df_filtered_type.withColumn(
    "lon", trim(split(col("coords"), ",").getItem(0)).cast("float")
).withColumn(
    "lat", trim(split(col("coords"), ",").getItem(1)).cast("float")
).filter(
    (col("lat") >= 5) & (col("lat") <= 21) & 
    (col("lon") >= 97) & (col("lon") <= 105)
)

BANGKOK_PROVINCE_NAMES = ["กรุงเทพมหานคร", "กรุงเทพ", "จังหวัดกรุงเทพมหานคร"]
df_bangkok_only = df_final_spatial.filter(col("province").isin(BANGKOK_PROVINCE_NAMES))

# ---------------------------------------------------------------------------------------
# จัดการเรื่องเวลา (Timestamp)
df_trim_string = df_bangkok_only.withColumn(
    "timestamp_str", substring(col("timestamp"), 1, 19)
).withColumn(
    "last_activity_str", substring(col("last_activity"), 1, 19)
)

TIMESTAMP_FORMAT_SIMPLE = "yyyy-MM-dd HH:mm:ss"

df_time_prep = df_trim_string.withColumn(
    "timestamp_dt", to_timestamp(col("timestamp_str"), TIMESTAMP_FORMAT_SIMPLE)
).withColumn(
    "last_activity_dt", to_timestamp(col("last_activity_str"), TIMESTAMP_FORMAT_SIMPLE)
).filter(col("timestamp_dt").isNotNull())

df_time_prep = df_time_prep.withColumn("timestamp_date", to_date(col("timestamp_dt")))
df_time_prep = df_time_prep.withColumn("last_activity_date", to_date(col("last_activity_dt")))

df_final_ready = df_time_prep.withColumn(
    "DaysToFix",
    when(col("state") == "เสร็จสิ้น", datediff(col("last_activity_date"), col("timestamp_date")))
    .otherwise(datediff(to_date(current_timestamp()), col("timestamp_date")))
)

# --------------------------------------------------------------------------------
# ทำความสะอาด Comment
df_clean = (
    df_final_ready
    .withColumn("comment_clean", trim(col("comment")))
    .withColumn("comment_clean", lower(col("comment_clean")))
    .withColumn("comment_clean", regexp_replace(col("comment_clean"), "[\n\r\t]", " "))
    .withColumn("comment_clean", regexp_replace(col("comment_clean"), "[^ก-๙a-z0-9/. ]", ""))
    .withColumn("comment_clean", regexp_replace(col("comment_clean"), " +", " "))
)

MIN_COMMENT_LENGTH = 10
df_clean = df_clean.filter(length(col("comment_clean")) >= MIN_COMMENT_LENGTH)

# --------------------------------------------------------------------------------
# Deduplication (ลบข้อมูลซ้ำ)
df_grouped = df_clean.withColumn("micro_lat", floor(col("lat") * 10000)) \
                     .withColumn("micro_lon", floor(col("lon") * 10000)) \
                     .withColumn("comment_group", col("comment_clean"))

window_spec = Window.partitionBy("micro_lat", "micro_lon", "comment_group").orderBy(col("timestamp_dt").asc())
df_ranked = df_grouped.withColumn("rank", row_number().over(window_spec))
df_deduplicated_final = df_ranked.filter(col("rank") == 1).drop("micro_lat", "micro_lon", "comment_group", "rank")

# ------------------------------------------------------------------------------------------
# เลือก Column สุดท้าย
COLUMNS_TO_KEEP = [
    "ticket_id", "type", "address", "district",
    "lat", "lon", "DaysToFix", "comment_clean",
    "timestamp_dt", "last_activity_dt"
]

df_ready_for_export = df_deduplicated_final.select(*COLUMNS_TO_KEEP)
df_ready_for_export = df_ready_for_export.na.drop(subset=["comment_clean", "district"])
df_ready_for_export = df_ready_for_export.filter(col("district").isNotNull())

# ----------------------------------------------------------------------------------------------------
# One-Hot Encoding ประเภทปัญหา
df_multi_hot = df_ready_for_export
for t in livability_types:
    new_col_name = f"type_{t}"
    df_multi_hot = df_multi_hot.withColumn(
        new_col_name,
        when(col("type").contains(t), lit(1)).otherwise(lit(0))
    )

# ----------------------------------------------------------------------------------------------------
# เพิ่ม Year Column
df_final_year = df_multi_hot.withColumn("year_reported", year(col("timestamp_dt"))) \
                            .withColumn("year_last_activity", year(col("last_activity_dt")))

df_final_ml = df_final_year.drop("type") 
df_final_ml = df_final_ml.withColumnRenamed("DaysToFix", "DaysActive_Pending")

# ----------------------------------------------------------------------------------------------------
# Clean Newline ใน Text ก่อน Save (ป้องกัน CSV พัง)
string_cols_to_clean = ["comment_clean", "address", "district"] 
df_cleaned_for_export = df_final_ml 

for col_name in string_cols_to_clean:
    df_cleaned_for_export = df_cleaned_for_export.withColumn(
        col_name, regexp_replace(col(col_name), "[\r\n]", " ")
    )

print("--- Data Cleaning เสร็จสิ้น เตรียมบันทึกไฟล์ ---")

# 🔥 [ส่วนแก้ไขที่ 3] ใช้ Absolute Path สำหรับ Output
OUTPUT_PATH = r"C:\Year_2\DSDE\dsdengdeng-project-dsde\data\processed"

try:
    df_cleaned_for_export.coalesce(1).write.format("csv") \
                             .option("header", "true") \
                             .option("encoding", "UTF-8") \
                             .mode("overwrite") \
                             .option("quote", "\"")     \
                             .option("escape", "\"")    \
                             .save(OUTPUT_PATH)
    print(f"✅ บันทึกไฟล์สำเร็จ! ไฟล์อยู่ที่: {OUTPUT_PATH}")
except Exception as e:
    print(f"❌ เกิดข้อผิดพลาดตอนเซฟไฟล์: {e}")
    print("คำแนะนำ: ลองเช็คว่ามีไฟล์ winutils.exe หรือยัง หรือลองรัน terminal แบบ Administrator")