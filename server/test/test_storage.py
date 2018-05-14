import unittest

import sys
import os
import logging
import time

import sqlite3



sys.path.append("../")

from storage import SqliteGameHistory
from storage import hash_function



class TestSqliteGameHistory(unittest.TestCase):

    game_history = SqliteGameHistory()

    def setUp(self):
        FORMAT = "%(asctime)-15s %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=FORMAT)

    def tearDown(self):
        pass

    def test_store_steps_1(self):
        logging.info("test_user_itest_store_steps_1nfo_operation:")
        sqlite_file = "game_history_test.db"

        if os.path.isfile(sqlite_file):
            os.remove(sqlite_file)

        self.game_history.connect(sqlite_file)        
        self.assertEqual(os.path.isfile(sqlite_file), True)

        steps = [8, 4, 5, 7, 2, 3, 6, 1, 0] 


        self.game_history.store_steps(steps, 1, {})
        #test store same  steps
        self.game_history.store_steps(steps, 1, {})

        result = self.game_history.record_is_existing(steps)
        self.assertEqual(result, True)
        
        self.game_history.disconnect()

        # reopen db
        self.game_history.connect(sqlite_file)    
            
        self.assertEqual(os.path.isfile(sqlite_file), True)
        result = self.game_history.record_is_existing(steps)
        self.assertEqual(result, True)
        
        self.game_history.disconnect()

        # open db directly
        con = sqlite3.connect(sqlite_file)
        cur = con.cursor()
        steps_seq = str(steps)
        index = hash_function(steps_seq)
        # And this is the named style:
        cur.execute('select count(index_id) from steps_history where index_id=?', (index, ))
        count = cur.fetchone()
        self.assertEqual(count[0], 1)
        con.close()



if __name__ == '__main__':
    unittest.main()