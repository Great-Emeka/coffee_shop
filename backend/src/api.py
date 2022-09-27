import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# DROPS ALL RECORDS AND START NEW DB FROM SCRATCH
db_drop_and_create_all()

# ROUTES
# drinks api endpoint

@app.route('/drinks', methods=['GET'])
@requires_auth('get:drinks')
def get_drinks(payload):
    # getting all the drinks from db
    drinks = Drink.query.all()
    # return drinks message as jason
    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    }), 200


# Api endpoint to GET /drinks-detail
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_details(payload):
    # gets all the drinks from db
    drinks = Drink.query.all()
    # return jason body
    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in drinks]
    }), 200


# Endpoint for POSTing drinks
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    # get the body
    req = request.get_json()

    new_recipe = req['recipe']
    new_title = req['title']

    try:
        drink = Drink()
        drink.title = new_title
        # converting object to a string
        drink.recipe = json.dumps(new_recipe)
        # insert the new drink into DB
        drink.insert()

    except BaseException:
        abort(400)

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    }), 200


# updating drinks Api endpoint
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    # Get the body
    req = request.get_json()

    # Get the Drink with requested Id
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    # if no drink with given id abort
    if not drink:
        abort(404)

    try:

        requested_title = req.get('title')
        requested_recipe = req.get('recipe')

        # checking if the title is the one to be updated
        if requested_title:
            drink.title = requested_title

        # checking if the recipe is the one to be updated
        if requested_recipe:
            drink.recipe = json.dumps(req['recipe'])

        # update the drink
        drink.update()
    except Exception:
        abort(400)

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    }), 200


# Endpoint to DELETE with specific id
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    # Get the Drink with requested Id
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    # if no drink with given id abort
    if not drink:
        abort(404)

    try:
        # delete the drinkt
        drink.delete()
    except Exception:
        abort(400)

    return jsonify({
        'success': True,
        'delete': id
    }), 200


# All Possible Error Handling
'''
Error handler for 404 -Unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
Error handler for 404 - Resource not found
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource not found"
    }), 404


'''
Error handler for 405 - Method Not Allowed
'''


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": 'Method Not Allowed'
    }), 405


'''
Error handler for 400 - Bad Request
'''


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": 'Bad Request'
    }), 400


'''
Error handler for 401 - Unauthorized
'''


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": 'Unathorized'
    }), 401


'''
Error handler for 500 - Internal Server Error
'''


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": 'Internal Server Error'
    }), 500


'''
Error handler for AuthError
'''


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code