#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

@app.route("/")
def index():
    return "<h1>Code Challenge</h1>"

class RestaurantsResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return jsonify([restaurant.to_dict(only=("id", "name", "address")) for restaurant in restaurants])

class RestaurantResource(Resource):
    def get(self, id):
        restaurant = db.session.get(Restaurant, id) 
        if restaurant:
            return jsonify(restaurant.to_dict(rules=("-restaurant_pizzas.restaurant",)))
        
        return {"error": "Restaurant not found"}, 404

    def delete(self, id):
        restaurant = db.session.get(Restaurant, id) 
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return "", 204
        return jsonify({"error": "Restaurant not found"}), 404

class PizzasResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return jsonify([pizza.to_dict(only=("id", "name", "ingredients")) for pizza in pizzas])

class RestaurantPizzaResource(Resource):
    def post(self):
        data = request.get_json()
        price = data.get("price")
        pizza_id = data.get("pizza_id")
        restaurant_id = data.get("restaurant_id")

        if not isinstance(price, (int, float)) or not (1 <= price <= 30):
            return {"errors": ["validation errors"]}, 400  

        restaurant = db.session.get(Restaurant, restaurant_id)
        pizza = db.session.get(Pizza, pizza_id)

        if not restaurant or not pizza:
            return {"errors": ["validation errors"]}, 400 

        try:
            new_restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
            db.session.add(new_restaurant_pizza)
            db.session.commit()
            return new_restaurant_pizza.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return {"errors": ["validation errors"]}, 400  

api.add_resource(RestaurantsResource, "/restaurants")
api.add_resource(RestaurantResource, "/restaurants/<int:id>")
api.add_resource(PizzasResource, "/pizzas")
api.add_resource(RestaurantPizzaResource, "/restaurant_pizzas")  

if __name__ == "__main__":
    app.run(port=5555, debug=True)
