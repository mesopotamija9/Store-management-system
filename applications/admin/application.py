from flask import Flask, jsonify
from applications.configuration import Configuration
from applications.models import database, Product, OrderProduct, Category, ProductCategory
from flask_jwt_extended import JWTManager
from sqlalchemy import and_
from applications.roleCheck import roleCheck

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)


@application.route("/productStatistics", methods=["GET"])
@roleCheck(role="administrator")
def productStatistics():
    statistics = []
    ordersProducts = OrderProduct.query.all()

    for orderProduct in ordersProducts:
        product = {}
        p = Product.query.filter(Product.id == orderProduct.productId).first()
        i = 0
        while i < len(statistics):
            if statistics[i]["name"] == p.name:
                break
            i += 1

        if i < len(statistics):
            statistics[i]["sold"] += orderProduct.requested
            statistics[i]["waiting"] += orderProduct.requested - orderProduct.received
        else:
            product["name"] = p.name
            product["sold"] = orderProduct.requested
            product["waiting"] = orderProduct.requested - orderProduct.received
            statistics.append(product)

    return jsonify(statistics=statistics), 200


@application.route("/categoryStatistics", methods=["GET"])
@roleCheck(role="administrator")
def categoryStatistics():
    statistics = []
    categories = Category.query.all()

    for c in categories:
        category = {}
        category["name"] = c.name
        category["sold"] = 0
        productsCategory = ProductCategory.query.filter(ProductCategory.categoryId == c.id).all()
        for pc in productsCategory:
            ordersProducts = OrderProduct.query.filter(OrderProduct.productId == pc.productId)
            for op in ordersProducts:
                category["sold"] += op.requested

        statistics.append(category)

    sortedStatistics = sorted(statistics, key=lambda x: (-x["sold"], x["name"]))
    statistics = []
    for s in sortedStatistics:
        if s["name"] not in statistics:
            statistics.append(s["name"])

    return jsonify(statistics=statistics), 200

if (__name__ == "__main__"):
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5004)
