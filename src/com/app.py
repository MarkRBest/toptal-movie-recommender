#!flask/bin/python
from flask import Flask
from flask.helpers import make_response
from flask.json import jsonify
from flask.templating import render_template
import logging.config
import re
import time

from com.controller import Controller
from com.database import Database
from com.model import Model
import argparse

app = Flask(__name__)

global controller

error_codes = {0:"success", -1:"unknown error", -2: "client not found", -3: "movie_id invalid", -4: "invalid email", -5: "client_id exists", -6: "invalid name"}

@app.route('/')
@app.route('/index.html')
def index():
    fpath = 'index.html'
    return render_template(fpath)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/api/v1.0/add_client/<string:name>/<string:email>', methods=['GET'])
def add_client(name, email):
    global controller
    logger = logging.getLogger("webservice")
    code, client_id = controller.add_client(name, email)
    logger.debug("adding client name %s email %s code %d" % (name, email, code))
    return jsonify({"client_id": client_id, 'code': code, "result": error_codes[code]})

@app.route('/api/v1.0/client_history/<int:client_id>', methods=['GET'])
def get_client_history(client_id):
    global controller
    logger = logging.getLogger("webservice")
    code, history = controller.get_client_history(client_id)
    logger.debug("get_client_history: client_id %d code: %d  history: %s " % (client_id, code, history))
    return jsonify({'code': code, "client_id": client_id, "history": history})

@app.route('/api/v1.0/reset_client_history/<int:client_id>', methods=['GET'])
def reset_client_history(client_id):
    global controller
    logger = logging.getLogger("webservice")
    code = controller.reset_client_history(client_id)
    logger.debug("reset_client_history: client_id %d code: %d " % (client_id, code))
    return jsonify({'code': code, "client_id": client_id})

@app.route('/api/v1.0/add_movie/<int:client_id>/<int:movie_id>', methods=['GET'])
def add_movie(client_id, movie_id):
    global controller
    logger = logging.getLogger("webservice")
    code = controller.add_movie(client_id, movie_id)
    logger.debug("add_movie client_id %d movie_id %d code:%d" % (client_id, movie_id, code))
    return jsonify({'code': code, "result": error_codes[code]})

@app.route('/api/v1.0/recommend/<int:client_id>', methods=['GET'])
def recommend_movies(client_id):
    global controller
    logger = logging.getLogger("webservice")
    code, movies = controller.recommendations(client_id)
    logger.debug("recommend_movies %s %s" % (client_id, movies))
    return jsonify({'code': code, "result": movies})

@app.route('/api/v1.0/search_movies/<string:name>', methods=['GET'])
def searchMovies(name):
    global controller
    logger = logging.getLogger("webservice")
    movies = controller.search_movies(name)
    logger.debug("search movies %s %d" % (name, len(movies)))
    return jsonify({"movies": movies})

@app.route('/api/v1.0/all_movies/', methods=['GET'])
def allMovies():
    global controller
    logger = logging.getLogger("webservice")
    movies = controller.all_movies()
    logger.debug("all movies %d" % (len(movies)))
    return jsonify({"movies": movies})

@app.route('/api/v1.0/', methods=['GET'])
@app.route('/api/', methods=['GET'])
def list_api_routes():
    rules = set()
    for rule in app.url_map.iter_rules() :
        url = str(rule)
        if re.match("/api/v1.0/.*",  url) :
            rules.add(url)

    return jsonify({"routes" : sorted(list(rules))})

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Fit natural language parser')
    parser.add_argument('--port', dest="port", default=5000, type=int,
                        help='port number')
    parser.add_argument('--host', dest="host", default="127.0.0.1",
                        help='host ip')
    parser.add_argument('--debug', dest="debug", default=False, type=bool,
                        help='enable debug')
    args = parser.parse_args()

    logging.config.fileConfig('../../logging.conf')
    logger = logging.getLogger("webservice")
    logger.info("Starting webserver host %s port %d" % (args.host, args.port))

    # loading database and model
    start = time.clock()
    logger.info("Building Database")
    database = Database("../../data/")
    logger.info("Time spent building database is: %.2f seconds"% (time.clock() - start))
    start = time.clock()
    logger.info("Building Model")
    model = Model(database)
    logger.info("Time spent building model is: %.2f seconds"% (time.clock() - start))

    global controller
    controller = Controller(database, model)

    logger.info("Webservice running")
    app.run(host=args.host,port=args.port, debug=args.debug)
    