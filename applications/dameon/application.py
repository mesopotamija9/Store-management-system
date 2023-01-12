from flask import Flask
from applications.configuration import Configuration
from applications.models import database, Product, Category, ProductCategory, OrderProduct
from multiprocessing import Process
from redis import Redis
from sqlalchemy import and_
import time
import json

application = Flask(__name__)
application.config.from_object(Configuration)


# def checkNewProducts():
#     with Redis(host=Configuration.REDIS_HOST) as redis:
#         bytesList = redis.lpop(Configuration.REDIS_PRODUCTS_LIST)
#         if bytesList is not None:
#             product = json.loads(bytesList)
#
#             categories = product[0].split("|")
#             name = product[1]
#             quantity = int(product[2])
#             price = float(product[3])
#
#             database.init_app(application)
#
#             with application.app_context():
#                 database.create_all()
#                 p = Product.query.filter(Product.name == name).first()
#                 if p is None:
#                     p = Product(name=name, quantity=quantity, price=price)
#                     database.session.add(p)
#                     database.session.commit()
#                     # print(f"Added -> {p}")
#                     for category in categories:
#                         c = Category.query.filter(Category.name == category).first()
#                         # print(str(c))
#                         if c is None:
#                             c = Category(name=category)
#                             database.session.add(c)
#                             database.session.commit()
#                             # print(f"Added -> {c}")
#
#                         productCategory = ProductCategory(productId=p.id, categoryId=c.id)
#                         database.session.add(productCategory)
#                         database.session.commit()
#                         # print(f"Added -> {productCategory}")
#                 else:
#                     productCategories = ProductCategory.query.filter(ProductCategory.productId == p.id).all()
#                     categoriesInDb = []
#                     for pc in productCategories:
#                         categoriesInDb.append(Category.query.filter(Category.id == pc.categoryId).first().name)
#
#                     categories.sort()
#                     categoriesInDb.sort()
#
#                     if categories != categoriesInDb:
#                         pass
#                         # print(f"Data for ({p}) is not correct. ({p}) declined.")
#                     else:
#                         currentQuantity = p.quantity
#                         currentPrice = p.price
#                         deliveryQuantity = quantity
#                         deliveryPrice = price
#                         newPrice = (currentQuantity * currentPrice + deliveryQuantity * deliveryPrice) / (currentQuantity + deliveryQuantity)
#
#                         p.quantity += deliveryQuantity
#                         p.price = newPrice
#                         database.session.add(p)
#                         database.session.commit()
#                         # print(f"Updated -> {p}")
#
#                 ordersProducts = OrderProduct.query.filter(and_(OrderProduct.received != OrderProduct.requested, OrderProduct.productId == p.id)).all()
#
#
#                 for orderProduct in ordersProducts:
#                     diff = orderProduct.requested - orderProduct.received
#                     if p.quantity != 0:
#                         if p.quantity >= diff:
#                             orderProduct.received += diff
#                             p.quantity -= diff
#                         else:
#                             orderProduct.received += p.quantity
#                             p.quantity = 0
#                         database.session.add(orderProduct)
#                         database.session.add(p)
#                         database.session.commit()


def work():
    database.init_app(application)
    while True:
        with Redis(host=Configuration.REDIS_HOST) as redis:
            bytesList = redis.blpop(Configuration.REDIS_PRODUCTS_LIST, 0)
            product = json.loads(bytesList[1])
            categories = product[0].split("|")
            name = product[1]
            quantity = int(product[2])
            price = float(product[3])

            with application.app_context():
                # database.create_all()
                p = Product.query.filter(Product.name == name).first()
                if p is None:
                    p = Product(name=name, quantity=quantity, price=price)
                    database.session.add(p)
                    database.session.commit()
                    # print(f"Added -> {p}")
                    for category in categories:
                        c = Category.query.filter(Category.name == category).first()
                        # print(str(c))
                        if c is None:
                            c = Category(name=category)
                            database.session.add(c)
                            database.session.commit()
                            # print(f"Added -> {c}")

                        productCategory = ProductCategory(productId=p.id, categoryId=c.id)
                        database.session.add(productCategory)
                        database.session.commit()
                        # print(f"Added -> {productCategory}")
                else:
                    productCategories = ProductCategory.query.filter(ProductCategory.productId == p.id).all()
                    categoriesInDb = []
                    for pc in productCategories:
                        categoriesInDb.append(Category.query.filter(Category.id == pc.categoryId).first().name)

                    categories.sort()
                    categoriesInDb.sort()

                    if categories != categoriesInDb:
                        pass
                        # print(f"Data for ({p}) is not correct. ({p}) declined.")
                    else:
                        currentQuantity = p.quantity
                        currentPrice = p.price
                        deliveryQuantity = quantity
                        deliveryPrice = price
                        newPrice = (currentQuantity * currentPrice + deliveryQuantity * deliveryPrice) / (
                                    currentQuantity + deliveryQuantity)

                        p.quantity += deliveryQuantity
                        p.price = newPrice
                        database.session.add(p)
                        database.session.commit()
                        # print(f"Updated -> {p}")

                ordersProducts = OrderProduct.query.filter(
                    and_(OrderProduct.received != OrderProduct.requested, OrderProduct.productId == p.id)).all()

                for orderProduct in ordersProducts:
                    diff = orderProduct.requested - orderProduct.received
                    if p.quantity != 0:
                        if p.quantity >= diff:
                            orderProduct.received += diff
                            p.quantity -= diff
                        else:
                            orderProduct.received += p.quantity
                            p.quantity = 0
                        database.session.add(orderProduct)
                        database.session.add(p)
                        database.session.commit()


if (__name__ == "__main__"):
    database.init_app(application)

    p = Process(target=work)
    p.start()
    application.run(debug=True, host="0.0.0.0", port=5002, use_reloader=False)
    p.join()
