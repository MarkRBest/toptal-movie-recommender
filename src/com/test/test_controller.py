'''
Test cases for the controller
'''
import unittest

from com.controller import Controller
from com.database import Database
from com.model import Model

database = Database("../../../data/")
model = Model(database)

class ModelTests(unittest.TestCase):

    def setUp(self):
        self.controller = Controller(database, model)

    def tearDown(self):
        pass

    def testAddClient(self):
        code, cid = self.controller.add_client("mark", "test.email@yahoo.com")
        self.assertEqual(code, 0)
        code, history = self.controller.get_client_history(cid)
        self.assertEqual(len(history), 0)

    def testAddClientHistory(self):
        code, cid = self.controller.add_client("mark", "test.email@yahoo.com")
        self.assertEqual(code, 0)
        self.controller.add_movie(cid, 285)
        self.controller.add_movie(cid, 1995)
        code, history = self.controller.get_client_history(cid)
        ids, names = zip(*history)
        self.assertTrue(285 in ids)
        self.assertTrue(1995 in ids)

    def testRecs(self):
        code, cid = self.controller.add_client("mark", "test.email@yahoo.com")
        self.controller.add_movie(cid, 285)
        code, recs = self.controller.recommendations(cid)
        self.assertEqual(len(recs), 5)

    def testMovieSearch(self):
        recs = self.controller.search_movies("avatar")
        self.assertEqual(len(recs), 1)
        recs = self.controller.search_movies("wsdgsdkjhgbkbjsdfg")
        self.assertEqual(len(recs), 0)
        recs = self.controller.search_movies("")
        self.assertEqual(len(recs), 0)

    def testAllMovies(self):
        recs = self.controller.all_movies()
        self.assertTrue(len(recs)> 0)

    def testResetHistory(self):
        code, client_id = self.controller.add_client("mark", "test.email@yahoo.com")
        self.assertEqual(code, 0)

        # add first movie
        self.controller.add_movie(client_id, movie_id=675)
        code, history = self.controller.get_client_history(client_id)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0][0], 675)

        # remove movies
        self.controller.reset_client_history(client_id)

        #
        self.controller.add_movie(client_id, movie_id=674)
        code, history = self.controller.get_client_history(client_id)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0][0], 674)

    def testRecommendWithNoHistory(self):
        code, client_id = self.controller.add_client("mark", "test.email@yahoo.com")
        self.assertEqual(code, 0)

        code, recs = self.controller.recommendations(client_id)
        self.assertEqual(len(recs), 5)



if __name__ == '__main__':
    unittest.main()