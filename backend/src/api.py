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

db_drop_and_create_all()

# ROUTES
'''
    implement endpoint
    GET /drinks
'''

@app.after_request
def after_request(response):
    response.headers.add(
      'Access-Control-Allow-Headers', 'Content-Type,Authorization,True'
      )
    response.headers.add(
      'Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS'
      )
    return response


@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        drinks = Drink.query.order_by('id').all()
        short_drinks = [drink.short() for drink in drinks]
        return jsonify({
            'success': True,
            'drinks': short_drinks,
            'total_drinks': len(drinks)
        })
    except:
        abort (404)



'''
    implement endpoint
    GET /drinks-detail
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    try:
        drinks = Drink.query.order_by('id').all()
        long_drinks = [drink.long() for drink in drinks]
        return jsonify({
                'success': True,
                'drinks': long_drinks,
                'total_drinks': len(drinks)
            })
    except:
        abort(404)



'''
    implement endpoint
    POST /drinks
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(payload):
    body = request.get_json()
    dr_title = body.get('title', None)
    dr_recipe = body.get('recipe', None)

    try:
        drink = Drink(title=dr_title, recipe=dr_recipe)
        drink.insert()

        new_drink = Drink.query.filter(Drink.id == drink.id).one_or_none()
        new_drink = [new_drink.long()]
        return jsonify({
            'success': True,
            'drinks': new_drink
        })
    except:
        abort(422)

'''
    implement endpoint
    PATCH /drinks/<id>
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    body = request.get_json()
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink is None:
            abort(404)

        if 'recipe' in body:
            drink.recipe = body.get('recipe')
        elif 'title' in body:
            drink.title = body.get('title')
        else:
            abort(422)

        drink.update()

        current_drink = [drink.long()]
        return jsonify({
            'success': True,
            'drinks': current_drink
        }), 200
    except:
        abort(400)

        
'''
    implement endpoint
    DELETE /drinks/<id>
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404)
    try:
        drink.delete
        return jsonify({
            'success': True,
            'delete': id
        })
    except:
        abort(400)


# Error Handling
'''
    Example error handling for unprocessable entity
'''

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable"
    }), 422


'''
    implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource Not Found"
        }), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad Request'
    }), 400

@app.errorhandler(405)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'Method Not Allowed'
    }), 405

@app.errorhandler(500)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Internal Server Error'
    }), 500

'''
    implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': error.error['description'],
        'code': error.error['code']
    }), error.status_code

