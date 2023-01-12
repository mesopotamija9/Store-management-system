from flask import Flask
from configuration import Configuration
from flask_migrate import Migrate, init, migrate, upgrade
from models import database, Role, UserRole, User
from sqlalchemy_utils import database_exists, create_database

application = Flask(__name__)
application.config.from_object(Configuration)

migrateObject = Migrate(application, database)

done = False

while not done:
    try:
        if not database_exists(application.config["SQLALCHEMY_DATABASE_URI"]):
            create_database(application.config["SQLALCHEMY_DATABASE_URI"])

        database.init_app(application)

        with application.app_context() as context:
            init()
            migrate(message="Deployment migration")
            upgrade()

            adminRole = Role(name="administrator")
            customerRole = Role(name="customer")
            warehouseRole = Role(name="manager")

            database.session.add(adminRole)
            database.session.add(customerRole)
            database.session.add(warehouseRole)
            database.session.commit()

            admin = User(
                email="admin@admin.com",
                password="1",
                forename="admin",
                surname="admin"
            )

            database.session.add(admin)
            database.session.commit()

            userRole = UserRole(
                userId=admin.id,
                roleId=adminRole.id
            )

            database.session.add(userRole)
            database.session.commit()

            done = True
    except Exception as e:
        print(e)