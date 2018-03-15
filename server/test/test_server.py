"""
curl -i -X POST -H "Content-Type:application/json" http://localhost:5000/start   -d "{'userName':'TEST1'}" 
curl -i -X POST -H "Content-Type:application/json" http://localhost:5000/predict -d '{"userName":"DEMO1","dataset":[[200,27,102,80,-36,80,579,66,21,61,208,71,-110]]}'
"""



import os
import sys
import unittest
import json
import logging


sys.path.append("../")

import server

class FlaskServerTest(unittest.TestCase):

    def setUp(self):
        self.client = server.app.test_client()

    def tearDown(self):
        pass

    def test_register_login(self):
        logging.debug("test_start:")
        response = self.client.post('/start', 
        data=json.dumps({"userName":"DEMO1", "password":"12345"})
        , content_type='application/json'
        , follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    

if __name__ == '__main__':
    server.init_log()
    unittest.main()