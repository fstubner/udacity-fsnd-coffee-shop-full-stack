from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import setup_db, db_drop_and_create_all, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@[DONE] TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()


@app.route('/drinks')
def get_drinks():
    '''
    @[DONE] TODO implement endpoint
        GET /drinks
            it should be a public endpoint
            it should contain only the drink.short() data representation
        returns status code 200 and json {"success": True, "drinks": drinks}
        where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    '''

    try:
        return jsonify({
            "success": True,
            "drinks": [drink.short() for drink in Drink.query.all()]
        }), 200

    except exc.SQLAlchemyError as e:
        print(e)
        abort(400)


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    '''
    @[DONE] TODO implement endpoint
        GET /drinks-detail
            it should require the 'get:drinks-detail' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drinks}
        where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    '''

    try:
        return jsonify({
            "success": True,
            "drinks": [drink.long() for drink in Drink.query.all()]
        }), 200

    except exc.SQLAlchemyError as e:
        print(e)
        abort(400)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(jwt):
    '''
    @[DONE] TODO implement endpoint
        POST /drinks
            it should create a new row in the drinks table
            it should require the 'post:drinks' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the newly created drink
            or appropriate status code indicating reason for failure
    '''

    data = request.get_json()

    try:
        drink = Drink(
            title=data.get('title'),
            recipe=json.dumps(data.get('recipe'))
        )
        drink.insert()

        return jsonify({
            "success": True,
            "drinks": [drink.long() for drink in Drink.query
                       .filter(Drink.id == drink.id).all()]
        }), 200

    except exc.SQLAlchemyError as e:
        print(e)
        abort(400)


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt, id):
    '''
    @[DONE] TODO implement endpoint
        PATCH /drinks/<id>
            where <id> is the existing model id
            it should respond with a 404 error if <id> is not found
            it should update the corresponding row for <id>
            it should require the 'patch:drinks' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the updated drink
            or appropriate status code indicating reason for failure
    '''
    data = request.get_json()

    title = data.get('title', None)
    recipe = data.get('recipe', None)

    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()

        if not drink:
            abort(404)

        if title:
            drink.title = title

        if recipe:
            drink.recipe = json.dumps(recipe)

        drink.update()

        return jsonify({
            "success": True,
            "drinks": [drink.long() for drink in Drink.query
                       .filter(Drink.id == drink.id).all()]
        })

    except exc.SQLAlchemyError as e:
        print(e)
        abort(400)


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):
    '''
    @[DONE] TODO implement endpoint
        DELETE /drinks/<id>
            where <id> is the existing model id
            it should respond with a 404 error if <id> is not found
            it should delete the corresponding row for <id>
            it should require the 'delete:drinks' permission
        returns status code 200 and json {"success": True, "delete": id} where
        id is the id of the deleted record
            or appropriate status code indicating reason for failure
    '''
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()

        if not drink:
            abort(404)

        drink.delete()

        return jsonify({
            "success": True,
            "delete": id
        })

    except exc.SQLAlchemyError as e:
        print(e)
        abort(400)


#
# Error Handling
###############################################


@app.errorhandler(422)
def unprocessable(error):
    '''
    Example error handling for unprocessable entity
    '''
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@[DONE] TODO implement error handlers using the @app.errorhandler(error)
decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


@app.errorhandler(404)
def resource_not_found(error):
    '''
    @[DONE] TODO implement error handler for 404
        error handler should conform to general task above
    '''
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(AuthError)
def auth_error(error):
    '''
    @[DONE] TODO implement error handler for AuthError
        error handler should conform to general task above
    '''
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
    }), error.status_code
