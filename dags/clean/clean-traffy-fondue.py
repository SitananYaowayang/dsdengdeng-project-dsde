from functools import reduce
from pyspark.sql.functions import (col, trim, lower, regexp_replace, sum, udf, to_timestamp,split, datediff, substring, length,
    current_timestamp, when, datediff,lit, year,try_to_timestamp, to_date,floor, row_number, min)
from pythainlp import word_tokenize
from pyspark.sql.types import ArrayType, StringType
from pythainlp.corpus import thai_stopwords
from pyspark.sql.window import Window

spark_url = 'local'
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType

spark = SparkSession.builder \
    .appName("TraffyFondueDataCleaning") \
    .config("spark.executor.memory", "4g") \
    .config("spark.driver.memory", "4g") \
    .getOrCreate()

sc = spark.sparkContext
file_path = r'C:\Users\sasit\CU\2-1\dsde\project\dsdengdeng-project-dsde\data\raw\traffy-fondue\bangkok_2025-12.csv'

# ----------------------------------------------------------------------------------------------------


traffy_schema = StructType([
    # ตัวระบุเฉพาะ
    StructField("ticket_id", StringType(), True),
    
    # ข้อมูลปัญหาและการจัดการ
    StructField("type", StringType(), True),         # หมวดหมู่ปัญหา
    StructField("organization", StringType(), True), # หน่วยงานที่รับผิดชอบ
    StructField("comment", StringType(), True),      # ข้อความร้องเรียน (สำคัญสำหรับ LLM)
    StructField("photo", StringType(), True),
    StructField("photo_after", StringType(), True),
    
    # ข้อมูลพิกัดและตำแหน่ง
    StructField("coords", StringType(), True),       # พิกัด Lat/Long (เก็บเป็น String ก่อนแล้วค่อย Parse)
    StructField("address", StringType(), True),
    StructField("subdistrict", StringType(), True),
    StructField("district", StringType(), True),
    StructField("province", StringType(), True),
    
    # ข้อมูลเวลาและสถานะ
    StructField("timestamp", StringType(), True),    # วันที่สร้าง (เก็บเป็น String ก่อนแล้วค่อย Cast เป็น Timestamp)
    StructField("state", StringType(), True),        # สถานะปัจจุบัน (ใช้ในการ Filter Active Issues)
    
    # ข้อมูลการตอบรับและกิจกรรม
    StructField("star", FloatType(), True),          # เรทติ้ง 0-5
    StructField("count_reopen", IntegerType(), True), # จำนวนครั้งที่เปิดซ้ำ
    StructField("last_activity", StringType(), True)  # วันที่กิจกรรมล่าสุด (เก็บเป็น String ก่อน)
])



df_traffy = spark.read.csv(
    file_path,
    header=True,
    schema=traffy_schema,
    multiLine=True, # สำคัญ: หาก 'comment' หรือ 'address' มีหลายบรรทัด
    escape='"' # สำคัญ: หากมีเครื่องหมายคำพูดในข้อความ
)



# ------------------------------------------------------------------

# ลิสต์หมวดหมู่หลักที่ส่งผลต่อมูลค่าอสังหาฯ และความน่าอยู่
livability_types = [
    "ถนน",
    "ทางเท้า",
    "ความปลอดภัย",
    "แสงสว่าง",
    "ความสะอาด",
    "กีดขวาง",
    "ท่อระบายน้ำ",
    "น้ำท่วม",
    "ต้นไม้",
    "PM2",
    "จราจร",
    "สะพาน"
]

# กรองข้อมูลตาม 'type' (หมวดหมู่ปัญหา)
# ใช้วิธี 'isin' ที่ตรงไปตรงมาที่สุด
df_filtered_type = df_traffy.filter(
    reduce(lambda a, b: a | b, [col("type").contains(t) for t in livability_types])
)

active_states = [
    "กำลังดำเนินการ",
    "รอรับเรื่อง" 
]



df_filtered_type = df_filtered_type.withColumn(
    "state", trim(col("state"))
)

df_filtered_type = df_filtered_type.filter(
    col("state").isin(active_states)
)
# print(f"จำนวนแถวหลังการกรองที่ใช้ในการวิเคราะห์: {df_filtered_type.count()}")



# ------------------------------------------------------------------
# กรองพิกัดเอาแค่กรุงเทพ 
df_final_spatial = df_filtered_type.withColumn(
    "lon_raw", 
    trim(split(col("coords"), ",").getItem(0)).cast("float")
).withColumn(
    "lat_raw", 
    trim(split(col("coords"), ",").getItem(1)).cast("float")
).withColumn(
    # Set the corrected columns
    "lon", col("lon_raw")
).withColumn(
    "lat", col("lat_raw")
).filter(
    # Filter for valid Thai coordinates (Roughly: lat between 5-21, lon between 97-105)
    (col("lat") >= 5) & (col("lat") <= 21) & 
    (col("lon") >= 97) & (col("lon") <= 105)
)
BANGKOK_PROVINCE_NAMES = ["กรุงเทพมหานคร", "กรุงเทพ","จังหวัดกรุงเทพมหานคร"]

# ใช้ df_final_spatial เป็น DataFrame ที่มีคอลัมน์ 'province'
df_bangkok_only = df_final_spatial.filter(
    col("province").isin(BANGKOK_PROVINCE_NAMES)
)

# # ตรวจสอบจำนวนแถวหลังการกรอง
# print(f"จำนวน Ticket ทั้งหมดในกรุงเทพมหานคร (รวมชื่อย่อ): {df_bangkok_only.count()}")

# # ตรวจสอบว่าคอลัมน์ province เหลือแต่ชื่อที่เราต้องการเท่านั้น
# print("การกระจายตัวของค่า 'province' หลังการกรอง:")
# df_bangkok_only.groupBy("province").count().show()



# ---------------------------------------------------------------------------------------
# แก้เวลา 
df_trim_string = df_bangkok_only.withColumn(
    "timestamp_str", 
    substring(col("timestamp"), 1, 19) # เริ่มจาก index 1, เอา 19 ตัวอักษร
).withColumn(
    "last_activity_str", 
    substring(col("last_activity"), 1, 19) # ทำเหมือนกันกับ last_activity
)

# Format ที่ใช้หลังตัด:
TIMESTAMP_FORMAT_SIMPLE = "yyyy-MM-dd HH:mm:ss"

# 2. แปลง String เป็น Timestamp (TimestampType)
df_time_prep = df_trim_string.withColumn(
    "timestamp_dt", 
    to_timestamp(col("timestamp_str"), TIMESTAMP_FORMAT_SIMPLE)
).withColumn(
    "last_activity_dt", 
    to_timestamp(col("last_activity_str"), TIMESTAMP_FORMAT_SIMPLE)
)

# กรองแถวที่แปลง timestamp ไม่ได้ (Timestamp/last_activity เป็น NULL หลังแปลง)
df_time_prep = df_time_prep.filter(
    col("timestamp_dt").isNotNull() 
)

# 3. แปลงเป็น Date และคำนวณ DaysToFix
df_time_prep = df_time_prep.withColumn("timestamp_date", to_date(col("timestamp_dt")))
df_time_prep = df_time_prep.withColumn("last_activity_date", to_date(col("last_activity_dt")))

df_final_ready = df_time_prep.withColumn(
    "DaysToFix",
    when(
        # ถ้า state = 'เสร็จสิ้น'
        col("state") == "เสร็จสิ้น",
        datediff(col("last_activity_date"), col("timestamp_date"))
    ).otherwise(
        # ถ้า state = 'กำลังดำเนินการ' หรือ 'รอรับเรื่อง'
        datediff(to_date(current_timestamp()), col("timestamp_date"))
    )
)

# # ตรวจสอบผลลัพธ์
# df_final_ready.select(
#     "ticket_id", "state", "lat", "lon", 
#     "timestamp_dt", "last_activity_dt", "DaysToFix","timestamp_date", "last_activity_date"
# ).show(5, truncate=False)



#--------------------------------------------------------------------------------
# ทำความสะอาดข้อความ comment

df_clean = (
    df_final_ready
    .withColumn("comment_clean", trim(col("comment")))
    .withColumn("comment_clean", lower(col("comment_clean")))
    .withColumn("comment_clean", regexp_replace(col("comment_clean"), "[\n\r\t]", " "))
    .withColumn("comment_clean", regexp_replace(col("comment_clean"), "[^ก-๙a-z0-9/. ]", ""))
    .withColumn("comment_clean", regexp_replace(col("comment_clean"), " +", " "))
)

MIN_COMMENT_LENGTH = 10
df_clean = df_clean.filter(
    (length(col("comment_clean")) >= MIN_COMMENT_LENGTH)
)
# print(df_clean.count())
# df_clean.show(20, truncate=False)

#--------------------------------------------------------------------------------
# จัดกลุ่มตามปัญหาที่คล้ายกันและพิกัดที่อยู่ใกล้กัน



# 1. กำหนดความละเอียดของพิกัด (Lat/Lon)
# การคูณด้วย 10,000 และใช้ floor จะทำให้ Lat/Lon มีความละเอียดประมาณ 10-20 เมตร
df_grouped = df_clean.withColumn("micro_lat", floor(col("lat") * 10000)) \
                        .withColumn("micro_lon", floor(col("lon") * 10000)) \
                        .withColumn("comment_group", col("comment_clean")) # ใช้ comment_clean เป็นกลุ่มหลัก

# 2. จัดอันดับ Ticket ภายในกลุ่มที่ซ้ำกัน
# W: จัดกลุ่มตามพิกัดและข้อความที่เหมือนกัน
window_spec = Window.partitionBy("micro_lat", "micro_lon", "comment_group").orderBy(col("timestamp_dt").asc())

df_ranked = df_grouped.withColumn(
    "rank", 
    row_number().over(window_spec)
)

# 3. กรอง: เก็บเฉพาะ Ticket แรกที่ถูกรายงาน (rank = 1)
df_deduplicated_final = df_ranked.filter(col("rank") == 1).drop("micro_lat", "micro_lon", "comment_group", "rank")

# print(f"จำนวน Ticket ก่อน Deduplication: {df_clean.count()}")
# print(f"จำนวน Ticket หลัง Deduplication: {df_deduplicated_final.count()}")

# df_deduplicated_final.filter(col("district") == "พระโขนง").show(5)


# ------------------------------------------------------------------------------------------
# filterคอลัมน์ที่จะนำไปใช้ต่อ 

# คอลัมน์ที่เราต้องการเก็บไว้เท่านั้น
COLUMNS_TO_KEEP = [
    "ticket_id",
    "type",
    # "organization",
    # "state",
    "address",
    "district",
    
    # Core features
    "lat",
    "lon",
    "DaysToFix",
    
    # Text Input for LLM
    "comment_clean",
    
    # Time Analysis (DateTimes)
    "timestamp_dt",
    "last_activity_dt"
]

df_ready_for_export = df_deduplicated_final.select(*COLUMNS_TO_KEEP)
df_ready_for_export = df_ready_for_export.na.drop(subset=["comment_clean", "district"])
df_ready_for_export = df_ready_for_export.filter(
    col("district").isNotNull() 
)
# print(f"จำนวนคอลัมน์เดิม: {len(df_deduplicated_final.columns)}")
# print(f"จำนวนคอลัมน์ใหม่: {len(df_ready_for_export.columns)}")

# df_ready_for_export.printSchema()


# ----------------------------------------------------------------------------------------------------
# แปลงเป็นปัญหาเป็นตัวเลข





# ตอนนี้ DaysToFix และ is_fixed สามารถใช้เป็น Features ในโมเดลได้
# df_model_ready.select("DaysToFix", "is_fixed","state", "comment_clean").show(10)

df_multi_hot = df_ready_for_export

for t in livability_types:
    # สร้างชื่อคอลัมน์ใหม่ (เช่น type_ถนน)
    new_col_name = f"type_{t}"
    
    df_multi_hot = df_multi_hot.withColumn(
        new_col_name,
        # ถ้าคอลัมน์ 'type' ดั้งเดิม มีข้อความ 't' อยู่ ให้กำหนดค่าเป็น 1
        when(col("type").contains(t), lit(1)).otherwise(lit(0))
    )

# # --- ตรวจสอบผลลัพธ์ ---
# # เลือกคอลัมน์ type ดั้งเดิม และคอลัมน์ Multi-Hot ที่สร้างขึ้นใหม่
# selected_cols = ["ticket_id", "type"] + [f"type_{t}" for t in livability_types]
# selected_cols.pop(-3)
# selected_cols.append("type_PM25")
# df_multi_hot = df_multi_hot.withColumnRenamed("type_PM2", "type_PM25")

# df_multi_hot.select(*selected_cols).show(20, truncate=False)

# ----------------------------------------------------------------------------------------------------
#  สร้างคอลัมน์ year_reported and Year_last_activity


# สร้างคอลัมน์ 'year_reported' จาก timestamp_dt
df_final_year = df_multi_hot.withColumn(
    "year_reported", 
    year(col("timestamp_dt"))
)

# สร้างคอลัมน์ 'year_last_activity' จาก last_activity_dt
df_final_year = df_final_year.withColumn(
    "year_last_activity", 
    year(col("last_activity_dt"))
)

# ----------------------------------------------------------------------------------------------------
df_final_ml = df_final_year.drop("type") 
# ถ้าคุณสร้างคอลัมน์ 'type_clean' ชั่วคราวในการแก้ไขปัญหา ก็ควรลบคอลัมน์นั้นด้วย
# df_final_ml = df_multi_hot.drop("type", "state", "type_clean") 
df_final_ml = df_final_ml.withColumnRenamed("DaysToFix", "DaysActive_Pending")


# ----------------------------------------------------------------------------------------------------
# clean comment




# 1. กำหนดคอลัมน์ที่เป็น String และมีโอกาสเกิด Newline
# ให้ใส่ชื่อคอลัมน์ที่เป็นข้อความขนาดใหญ่ทั้งหมดที่คุณมี (เช่น comment_clean, address)
string_cols_to_clean = ["comment_clean", "address", "district"] 

# 2. ทำการวนซ้ำเพื่อแทนที่อักขระ Newline ในทุกคอลัมน์
df_cleaned_for_export = df_final_ml 

for col_name in string_cols_to_clean:
    # แทนที่อักขระขึ้นบรรทัดใหม่ (\n) และ Carriage Return (\r) ด้วยช่องว่าง ' '
    df_cleaned_for_export = df_cleaned_for_export.withColumn(
        col_name,
        regexp_replace(col(col_name), "[\r\n]", " ")
    )

print("--- ล้างอักขระขึ้นบรรทัดใหม่เสร็จสิ้น ---")
# 3. ใช้ DataFrame นี้ในการบันทึกไฟล์
OUTPUT_PATH = r"C:\Users\sasit\CU\2-1\dsde\project\dsdengdeng-project-dsde\data\processed\traffy-fondue"

df_cleaned_for_export.coalesce(1).write.format("csv") \
                             .option("header", "true") \
                             .option("encoding", "UTF-8") \
                             .mode("overwrite") \
                             .option("quote", "\"")     \
                             .option("escape", "\"")    \
                             .save(OUTPUT_PATH)
print("Subset test save complete with UTF-8 encoding.")


# ----------------------------------------------------------------------------------------------------





