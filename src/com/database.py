'''
Database of movie information
'''

from datetime import date
import json
from string import lower

import pandas as pd
from nltk.stem.porter import PorterStemmer


class Database :

    def __init__(self, fpath):
        
        self.__movie_db = pd.read_csv(fpath + "tmdb_5000_movies.csv")

        self.__movie_genres = {}
        self.__movie_keywords = {}

        self.pre_process()

    def pre_process(self):
        '''
        raw dataset need to be processed to extract directors, actors and key words from json strings
        to improve performance and simplify machine learning code
        '''
        movie_data = self.__movie_db

        # add empty columns
        add_columns = ["director","producer","character1","character2","character3","actor1","actor2","actor3"]
        movie_data["year"] = 0
        for col in add_columns :
            movie_data[col] = ""

        stemmer = PorterStemmer()

        # populate default columns with relevant information
        for idx in movie_data.index:
            row = movie_data.iloc[idx]
            movie_id = row["id"]

            genres, keywords = [], []

            try :
                # parse year
                try:
                    year = int(row['release_date'][:4])
                    if 1900 < year < date.today().year + 1 :
                        movie_data.loc[idx, "year"] = year
                    else:
                        print "year could not be parsed '"'%s'"', '"'%s'"'" % (row['title'], row['release_date'])
                except :
                    print "year could not be parsed '"'%s'"', '"'%s'"'" % (row['title'], row['release_date'])

                # get director and producer
                crew = json.loads(row['crew'])
                for member in crew :
                    if lower(member['job']) == "director" :
                        movie_data.loc[idx, "director"] = member["name"]
                    if lower(member['job']) == "producer" :
                        movie_data.loc[idx, "producer"] = member["name"]
                del crew

                # get first 3 actors and charachters
                cast = json.loads(row["cast"])
                if len(cast) > 0 :
                    movie_data.loc[idx, "character1"] = cast[0]["character"]
                    movie_data.loc[idx, "actor1"] = cast[0]["name"]
                if len(cast) > 1 :
                    movie_data.loc[idx, "character2"] = cast[1]["character"]
                    movie_data.loc[idx, "actor2"] = cast[1]["name"]
                if len(cast) > 2 :
                    movie_data.loc[idx, "character3"] = cast[2]["character"]
                    movie_data.loc[idx, "actor3"] = cast[2]["name"]
                del cast

                # unpack genres
                json_genres = json.loads(row["genres"])
                for genre in json_genres :
                    genres.append(genre["name"])
                del json_genres

                # unpack keywords
                json_keywords = json.loads(row["keywords"])
                for keyword in json_keywords :
                    # stem the keywords so they are more likely to match other movies
                    keywords.append(stemmer.stem(keyword["name"]))
                del json_keywords

                self.__movie_keywords[movie_id] = keywords
                self.__movie_genres[movie_id] = genres

            except :
                print "cant process", row["id"], row["title"]

        # remove redundant columns
        self.__movie_db = movie_data[['id', 'title', 'year', 'director', 'producer', "original_language", "revenue", "budget", "vote_average", "vote_count", "popularity", "runtime",  "character1", "character2", "character3", "actor1", "actor2", "actor3"]]

    def getMovieData(self):
        return self.__movie_db

    def getGenres(self):
        return self.__movie_genres

    def getKeywords(self):
        return self.__movie_keywords

