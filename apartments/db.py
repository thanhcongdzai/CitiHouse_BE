from pymongo import MongoClient
from django.conf import settings
import os

MONGO_URI = "mongodb+srv://cong10112003:P7TCL8WxcffbY5RJ@citihouse.aypbw1k.mongodb.net/?appName=CitiHouse"
DB_NAME = "CitiHouse_MVP"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
apartments_collection = db['apartments']
users_collection = db['Users']
deposit_orders_collection = db['deposit_orders']
viewing_appointments_collection = db['viewing_appointments']
projects_collection = db['Projects']
password_resets_collection = db['password_resets']
