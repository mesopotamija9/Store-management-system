from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()


class ProductCategory(database.Model):
    __tablename__ = "productcategory"

    id = database.Column(database.Integer, primary_key=True)
    productId = database.Column(database.Integer, database.ForeignKey("product.id"), nullable=False)
    categoryId = database.Column(database.Integer, database.ForeignKey("category.id"), nullable=False)

    def __repr__(self):
        return f"ProductCategory: productId-{self.productId}, categoryId-{self.categoryId}"


class OrderProduct(database.Model):
    __tablename__ = "orderproduct"

    id = database.Column(database.Integer, primary_key=True)
    orderId = database.Column(database.Integer, database.ForeignKey("order.id"), nullable=False)
    productId = database.Column(database.Integer, database.ForeignKey("product.id"), nullable=False)
    productPrice = database.Column(database.Float, nullable=False)
    requested = database.Column(database.Integer, nullable=False)
    received = database.Column(database.Integer, nullable=False)

    def __repr__(self):
        return f"OrderProduct: orderId-{self.orderId}, productId-{self.productId}"

class Product(database.Model):
    __tablename__ = "product"

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False)
    quantity = database.Column(database.Integer, nullable=False)
    price = database.Column(database.Float, nullable=False)

    categories = database.relationship("Category", secondary=ProductCategory.__table__, back_populates="products")
    orders = database.relationship("Order", secondary=OrderProduct.__table__, back_populates="products")

    def __repr__(self):
        return f"Product: id-{self.id}, name-{self.name}, quantity-{self.quantity}, price-{self.price}"

class Category(database.Model):
    __tablename__ = "category"

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False)

    products = database.relationship("Product", secondary=ProductCategory.__table__, back_populates="categories")

    def __repr__(self):
        return f"Category: id-{self.id}, name-{self.name}"


class Order(database.Model):
    __tablename__ = "order"

    id = database.Column(database.Integer, primary_key=True)
    customerEmail = database.Column(database.String(256), nullable=False)
    timestamp = database.Column(database.DateTime, nullable=False)

    products = database.relationship("Product", secondary=OrderProduct.__table__, back_populates="orders")