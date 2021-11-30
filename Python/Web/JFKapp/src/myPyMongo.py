import os
import datetime

from pymongo import MongoClient


class PyMongoDB():

    def __init__(self):
        if not os.getenv('myMongoIP'):
            my_mongo_ip = "127.0.0.1"
        else:
            my_mongo_ip = os.getenv('myMongoIP')
        self.client = MongoClient(my_mongo_ip, 27017)
        db = self.client["howhow"]
        self.collection = db["JKF"]

    def find(self, number=0):
        get_list = self.collection.find({}).sort("dateTime", -1).limit(27).skip(number)
        ans = []
        for i in get_list:
            i.pop('_id')
            i.pop('dateTime')
            i.pop('createdAt')
            ans.append(i)
        return ans
