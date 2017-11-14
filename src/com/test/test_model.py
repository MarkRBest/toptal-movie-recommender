import unittest

from com.database import Database
from com.model import Model
import numpy as np

database = Database("../../../data/")
model = Model(database)

class ModelTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testSequel(self):
        self.assertEqual(model.isSequel(177572, 3131), 0)
        self.assertEqual(model.isSequel(672, 673), 1)

    def testJarquesDist(self):
        self.assertAlmostEqual(model.jarques_distance([0,0,0,0], [1,1,1,1]), 0.0, delta=0.0001)
        self.assertAlmostEqual(model.jarques_distance([0,1,0], [1,1,1]), 1.0/3.0, delta=0.0001)
        self.assertAlmostEqual(model.jarques_distance([1,1], [1,1]), 1.0, delta=0.0001)

    def testGetDistance(self):
        db = database.getMovieData()
        movie1 = db[db.id == 672].iloc[0]
        movie2 = db[db.id == 673].iloc[0]
        dist = model.getDistance(movie1, movie2)
        print dist
        print np.average(dist)
        self.assertNotEqual(dist, 0)

    def testRecommendEmpty(self):
        recs = model.getRecomendations([])
        self.assertNotEqual(len(recs), 0, "recs returned")

    def testRecommend(self):
        recs = model.getRecomendations([285])
        self.assertNotEqual(len(recs), 0, "recs returned")

if __name__ == '__main__':
    unittest.main()