from time import strftime

from flask import Flask, jsonify, request
from applications.configuration import Configuration
from applications.models import database, Category, Product, ProductCategory, Order, OrderProduct
from flask_jwt_extended import JWTManager, get_jwt_identity
from applications.roleCheck import roleCheck
from datetime import datetime

application = Flask(__name__)
application.config.from_object(Configuration)
jwt =JWTManager(application)


@application.route("/search", methods=["GET"])
@roleCheck(role="customer")
def search():
    name = ""
    category = ""
    for item in request.args.items():
        if str(item[0]) == "name":
            name = str(item[1])
        elif str(item[0]) == "category":
            category = str(item[1])

    categories = Category.query.filter(Category.name.like(f"%{category}%")).all()
    products = Product.query.filter(Product.name.like(f"%{name}%")).all()
    productIds = []
    for p in products:
        productIds.append(p.id)

    categoriesToReturn = []
    for c in categories:
        productCategories = ProductCategory.query.filter(ProductCategory.categoryId == c.id).all()
        for pc in productCategories:
            if pc.productId in productIds and c.name not in categoriesToReturn:
                categoriesToReturn.append(c.name)

    categoriesIds = []
    for c in categories:
        categoriesIds.append(c.id)

    productsToReturn = []
    for p in products:
        productCategories = ProductCategory.query.filter(ProductCategory.productId == p.id).all()
        for pc in productCategories:
            if pc.categoryId in categoriesIds and p not in productsToReturn:
                productsToReturn.append(p)

    jsonProducts = []
    for p in productsToReturn:
        productCategories = ProductCategory.query.filter(ProductCategory.productId == p.id).all()
        categories = []
        for pc in productCategories:
            categories.append(Category.query.filter(Category.id == pc.categoryId).first().name)
        jsonProducts.append(
            {"categories": categories, "id": p.id, "name": p.name, "price": p.price, "quantity": p.quantity}
        )

    return jsonify(categories=categoriesToReturn, products=jsonProducts), 200

    return name + "  " + category


@application.route("/order", methods=["POST"])
@roleCheck(role="customer")
def order():
    orderRequest = request.json.get("requests", "")

    if len(orderRequest) == 0:
        return jsonify(message="Field requests is missing."), 400

    i = 0
    for req in orderRequest:
        if "id" not in req:
            return jsonify(message=f"Product id is missing for request number {i}."), 400

        if "quantity" not in req:
            return jsonify(message=f"Product quantity is missing for request number {i}."), 400

        try:
            id = int(req["id"])
            if id <= 0:
                return jsonify(message=f"Invalid product id for request number {i}."), 400
        except ValueError:
            return jsonify(message=f"Invalid product id for request number {i}."), 400

        try:
            quantity = int(req["quantity"])
            if quantity <= 0:
                return jsonify(message=f"Invalid product quantity for request number {i}."), 400
        except ValueError:
            return jsonify(message=f"Invalid product quantity for request number {i}."), 400

        product = Product.query.filter(Product.id == id).first()
        if not product:
            return jsonify(message=f"Invalid product for request number {i}."), 400


        i += 1

    order = Order(customerEmail=get_jwt_identity(), timestamp=datetime.now())
    database.session.add(order)
    database.session.commit()

    for req in orderRequest:
        product = Product.query.filter(Product.id == int(req["id"])).first()
        requested = int(req["quantity"])
        received = 0
        if product.quantity >= requested:
            product.quantity -= requested
            received += requested
        else:
            received += product.quantity
            product.quantity = 0

        orderProduct = OrderProduct(orderId=order.id, productId=product.id, productPrice=product.price, requested=requested, received=received)
        database.session.add(orderProduct)
        database.session.add(product)
        database.session.commit()

    return jsonify(id=order.id), 200


@application.route("/status", methods=["GET"])
@roleCheck(role="customer")
def status():
    orders = Order.query.filter(Order.customerEmail == get_jwt_identity()).all()
    ordersResultArr = []
    for order in orders:
        orderResult = {}
        price = 0
        completed = True

        ordersProducts = OrderProduct.query.filter(OrderProduct.orderId == order.id).all()
        prodcuts = []
        for orderProduct in ordersProducts:
            productResult = {}
            categoriesObj = ProductCategory.query.filter(ProductCategory.productId == orderProduct.productId).all()
            categories = []
            for categoryObj in categoriesObj:
                categories.append(Category.query.filter(Category.id == categoryObj.categoryId).first().name)
            productResult["categories"] = categories
            productResult["name"] = Product.query.filter(Product.id == orderProduct.productId).first().name
            productResult["price"] = orderProduct.productPrice
            productResult["received"] = orderProduct.received
            productResult["requested"] = orderProduct.requested
            prodcuts.append(productResult)
            price += orderProduct.productPrice * orderProduct.requested
            if orderProduct.requested != orderProduct.received:
                completed = False

        orderResult["products"] = prodcuts
        orderResult["price"] = price
        if completed:
            orderResult["status"] = "COMPLETE"
        else:
            orderResult["status"] = "PENDING"

        orderResult["timestamp"] = order.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
        ordersResultArr.append(orderResult)



    return jsonify(orders=ordersResultArr), 200

if (__name__ == "__main__"):
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5003)
