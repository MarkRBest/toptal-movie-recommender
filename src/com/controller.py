from email.utils import parseaddr
import pickle
import re
from string import lower
import time
from validate_email import validate_email
import logging


class Controller :
    ''' Delegate for handling data access and routing '''

    def __init__(self, database, model):
        self.__client_emails = {}    # email:client_id
        self.__client_info = {}

        self.__client_history = {}

        self.__database = database
        self.__model = model

    def add_client(self, name, email):
        if name is None or len(name) == 0 :
            return -6, -1

        email = parseaddr(email)[1]
        if not validate_email(email, verify=True) :
            return -4, -1

        if email in self.__client_emails.keys() :
            return -5, -1

        client_id = len(self.__client_emails)+1
        self.__client_emails[email] = client_id
        self.__client_info[client_id] = [name, email]
        self.__client_history[client_id] = set()

        return 0, client_id

    def get_client_id(self, email):
        if self.__client_emails.has_key(email) :
            return self.__client_emails[email]
        else :
            return -1

    def get_client_history(self, client_id):
        if type(client_id) is not int :
            return -1, []

        if client_id in self.__client_history.keys() :
            history = list(self.__client_history[client_id])
            if history :
                # lookup film names
                db = self.__database.getMovieData()
                names = db[db.id.isin(history)].title
                return 0, zip(history, names)
            return 0, history
        else :
            return -2, []

    def reset_client_history(self, client_id):
        if type(client_id) is not int :
            return -1

        if client_id in self.__client_history.keys() :
            self.__client_history[client_id] = set()
            return 0
        else :
            return -2

    def add_movie(self, client_id, movie_id):
        if type(client_id) is not int or type(movie_id) is not int :
            return -1

        # validate movie
        all_ids = set(self.__database.getMovieData().id)
        if movie_id not in all_ids:
            return -3
        # validate client
        if client_id not in self.__client_history.keys():
            return -2

        self.__client_history[client_id].add(movie_id)
        return 0

    def recommendations(self, client_id):
        ''' get movie recomensations '''
        code, history = self.get_client_history(client_id)
        if code != 0 :
            return code, []

        # check if there was a client history
        if len(history) == 0 :
            movie_ids = history
        else :
            movie_ids, names = zip(*history)

        start = time.clock()
        recs = self.__model.getRecomendations(movie_ids)
        logger = logging.getLogger("webservice")
        logger.info("Time %.2f seconds" %(time.clock() - start))

        return 0, recs

    def search_movies(self, name) :
        ''' search for the id of movies with a given name '''
        if name is None or len(name) == 0 :
            return []

        db = self.__database.getMovieData()
        regex = re.compile(".*"+lower(name)+".*")
        db = db[map(lambda x: True if regex.match(lower(x)) is not None else False, db.title)]
        if len(db) == 0 :
            return []
        return zip(db.id, db.title)

    def all_movies(self):
        ''' get all pairs of movie and movie names '''
        db = self.__database.getMovieData()
        return zip(db.id, db.title)
