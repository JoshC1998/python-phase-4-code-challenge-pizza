#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
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
    return "<h1>Code challenge</h1>"

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([ restaurant.to_dict() for restaurant in  restaurants]), 200

@app.route('/restaurants/<int:id>', methods=['GET', 'DELETE']) 
def restaurant_by_id(id):
   
    restaurant = Restaurant.query.get(id)

    if restaurant is None:
        return jsonify({'error': 'Restaurant not found'}), 404

    if request.method == 'GET':
        restaurant_dict = restaurant.to_dict()
        restaurant_dict['restaurant_pizzas'] = []

        return jsonify(restaurant_dict), 200

    elif request.method == 'DELETE':
        db.session.delete(restaurant)
        db.session.commit()

        return jsonify({
            "delete_successful": True,
            "message": "Restaurant deleted."
        }), 204


@app.route('/pizzas')
def get_pizza(): #GET
    pizzas = [pizza.to_dict() for pizza in Pizza.query.all()]
    return make_response( pizzas, 200 )



@app.route('/restaurant_pizzas', methods=['GET', 'POST'])
def restaurant_pizzas():
    if request.method == 'GET':
        restaurant_pizzas = [pizza.to_dict() for pizza in RestaurantPizza.query.all()]
        return jsonify(restaurant_pizzas), 200

    elif request.method == 'POST':
        data = request.json
        try:
            if not data:
              return {'errors': ['validation errors']}, 400

        
            if not data['price']or not data['pizza_id'] or not data['restaurant_id']:
               return {'errors': ['validation errors']}, 400

        
            new_restaurant_pizza = RestaurantPizza(
                price=data["price"],
                pizza_id=data["pizza_id"],
                restaurant_id=data["restaurant_id"],
            )

            db.session.add(new_restaurant_pizza)
            db.session.commit()

            restaurant_pizza_dict = new_restaurant_pizza.to_dict()

            response = make_response(
                jsonify(restaurant_pizza_dict),
                201
            )
            return response
        except Exception as e:
            return make_response(jsonify({'errors': ['validation errors']}), 400)


if __name__ == "__main__":
    app.run(port=5555, debug=True)