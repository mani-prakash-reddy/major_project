from pyspark.sql import SparkSession
from pymongo import MongoClient
import requests
import time

model_endpoint = "http://localhost:5000/predict"

def get_prediction(features):
	response = requests.post(model_endpoint, json={"features":features})
	return response.json()["prediction"]

mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["project"]
db_collection = mongo_db["data"]


topic = "ids"
bootstrap_server_ip = "localhost"
server_port = 9092

spark = SparkSession.builder.appName("KafkaStream").getOrCreate()

df = spark.readStream.format("kafka").option("kafka.bootstrap.servers", f"{bootstrap_server_ip}:{server_port}").option("subscribe", topic).load()

def classify_insert(kafka_data):
    device_id = kafka_data.key.decode()
    kafka_data = kafka_data.value.decode().split(",")
    features = [float(x) for x in kafka_data]
    prediction = get_prediction(features)
    _ = db_collection.insert_one({"device_name":device_id,"raw_data": features, "remark":prediction})


df.writeStream.foreach(classify_insert).start()