import json

from flask import Flask, request, jsonify, Response
from applications.configuration import Configuration
from applications.models import database
from flask_jwt_extended import JWTManager
from applications.roleCheck import roleCheck
from redis import Redis
import io
import csv

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)


@application.route("/update", methods=["POST"])
@roleCheck(role="manager")
def update():
    file = request.files.get("file", "")

    if isinstance(file, str):
        return jsonify(message="Field file is missing."), 400

    content = file.stream.read().decode("utf-8")
    stream = io.StringIO(content)
    reader = csv.reader(stream)

    with Redis(host=Configuration.REDIS_HOST) as redis:
        data = []
        lineNumber = 0
        for line in reader:
            if len(line) != 4:
                return jsonify(message=f"Incorrect number of values on line {lineNumber}."), 400

            try:
                quantity = int(line[2])
                if quantity < 0:
                    return jsonify(message=f"Incorrect quantity on line {lineNumber}."), 400
            except ValueError:
                return jsonify(message=f"Incorrect quantity on line {lineNumber}."), 400

            try:
                price = float(line[3])
                if price < 0:
                    return jsonify(message=f"Incorrect price on line {lineNumber}."), 400
            except ValueError:
                return jsonify(message=f"Incorrect price on line {lineNumber}."), 400

            data.append(line)
            lineNumber += 1

        for product in data:
            # print(product)
            redis.rpush(Configuration.REDIS_PRODUCTS_LIST, json.dumps(product))

    return Response(status=200)


if (__name__ == "__main__"):
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5001)
