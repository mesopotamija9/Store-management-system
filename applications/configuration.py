import os

databaseUrl = os.environ["DATABASE_URL"]
redisHost = os.environ["REDIS_HOST"]

class Configuration():
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{databaseUrl}/store"
    REDIS_HOST = redisHost
    REDIS_PRODUCTS_LIST = "products5"
    JWT_SECRET_KEY = "MY_SECRET_JWT_KEY"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
