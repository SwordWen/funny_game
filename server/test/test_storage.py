import unittest

import sys
import os
import logging
import time

import sqlite3



sys.path.append("../")

from storage import SqliteGameHistory
from storage import hash_function
from storage import TreeMgr
from storage import convert_location

import function

#class TestSqliteGameHistory(unittest.TestCase):
class TestSqliteGameHistory:

    def setUp(self):
        FORMAT = "%(asctime)-15s %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=FORMAT)

    def tearDown(self):
        pass

    def test_store_steps_1(self):
        logging.info("test_user_itest_store_steps_1nfo_operation:")
        sqlite_file = "game_history_test.db"

        game_history = SqliteGameHistory()

        if os.path.isfile(sqlite_file):
            os.remove(sqlite_file)

        game_history.connect(sqlite_file)        
        self.assertEqual(os.path.isfile(sqlite_file), True)

        steps = [8, 4, 5, 7, 2, 3, 6, 1, 0] 


        game_history.store_steps(steps, 1, {})
        #test store same  steps
        game_history.store_steps(steps, 1, {})

        result = game_history.record_is_existing(steps)
        self.assertEqual(result, True)
        
        game_history.disconnect()

        # reopen db
        game_history.connect(sqlite_file)    
            
        self.assertEqual(os.path.isfile(sqlite_file), True)
        result = game_history.record_is_existing(steps)
        self.assertEqual(result, True)
        
        game_history.disconnect()

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

    def test_update_tree_nodes(self):
        logging.info("test_select_steps_from_history:")
        sqlite_file = "../sqlite_game_history.db"
        """
(u'[1, 0, 2, 3, 7, 6, 8, 4, 5]', 0)
(u'[7, 5, 6, 3, 0, 1, 2, 4, 8]', 0)
(u'[4, 6, 3, 8, 2, 7, 1, 5, 0]', 10)
(u'[2, 5, 7, 0, 4, 3, 6, 1, 8]', 10)
(u'[5, 8, 4, 0, 6, 2, 7, 3, 1]', 10)
(u'[0, 7, 8, 4, 1, 5, 6, 2, 3]', 10)
(u'[6, 3, 8, 0, 4, 5, 1, 2, 7]', 10)
(u'[8, 3, 0, 5, 7, 1, 6, 4, 2]', 0)
(u'[3, 1, 7, 8, 0, 5, 4, 2, 6]', 10)
(u'[3, 5, 7, 0, 1, 2, 8, 6, 4]', 10)
        """
        game_history = SqliteGameHistory()
        game_history.connect(sqlite_file) 
        game_history.store_steps([1, 0, 2, 3, 7, 6, 8, 4, 5], 0)
        game_history.store_steps([7, 5, 6, 3, 0, 1, 2, 4, 8], 0)
        game_history.store_steps([4, 6, 3, 8, 2, 7, 1, 5, 0], 10)
        game_history.store_steps([2, 5, 7, 0, 4, 3, 6, 1, 8], 10)
        game_history.store_steps([3, 1, 7, 8, 0, 5, 4, 2, 6], 10)
        game_history.store_steps([3, 5, 7, 0, 1, 2, 8, 6, 4], 10)
        game_history.disconnect()

    def test_select_steps_from_history(self):
        logging.info("test_select_steps_from_history:")
        sqlite_file = "../sqlite_game_history.db"

        game_history = SqliteGameHistory()
        game_history.connect(sqlite_file)  
        game_history.select_steps_from_history()
        game_history.disconnect()

class TestTreeMgr(unittest.TestCase):     

    def test_update_tree_nodes(self):
        logging.info("test_update_tree_nodes:")
        """
(u'[1, 0, 2, 3, 7, 6, 8, 4, 5]', 0)
(u'[7, 5, 6, 3, 0, 1, 2, 4, 8]', 0)
(u'[4, 6, 3, 8, 2, 7, 1, 5, 0]', 10)
(u'[2, 5, 7, 0, 4, 3, 6, 1, 8]', 10)
(u'[5, 8, 4, 0, 6, 2, 7, 3, 1]', 10)
(u'[0, 7, 8, 4, 1, 5, 6, 2, 3]', 10)
(u'[6, 3, 8, 0, 4, 5, 1, 2, 7]', 10)
(u'[8, 3, 0, 5, 7, 1, 6, 4, 2]', 0)
(u'[3, 1, 7, 8, 0, 5, 4, 2, 6]', 10)
(u'[3, 5, 7, 0, 1, 2, 8, 6, 4]', 10)
        """
        # update tree nodes
        tree_mgr = TreeMgr()
        tree_mgr.update_tree_nodes([1, 0, 2, 3, 7, 6, 8, 4, 5], 0)
        tree_mgr.update_tree_nodes([7, 5, 6, 3, 0, 1, 2, 4, 8], 0)
        tree_mgr.update_tree_nodes([4, 6, 3, 8, 2, 7, 1, 5, 0], 10)
        tree_mgr.update_tree_nodes([2, 5, 7, 0, 4, 3, 6, 1, 8], 10)
        tree_mgr.update_tree_nodes([3, 1, 7, 8, 0, 5, 4, 2, 6], 10)
        tree_mgr.update_tree_nodes([3, 5, 7, 0, 1, 2, 8, 6, 4], 10)

        tree_node1 = tree_mgr.get_tree_node([1])
        self.assertEqual(tree_node1.node_id, "1")
        self.assertEqual(tree_node1.height, 1)
        self.assertEqual(tree_node1.index, 1)
        self.assertEqual(tree_node1.get_prop("total"), 1)

        tree_node1 = tree_mgr.get_tree_node([3])
        self.assertTrue(tree_node1.above_threshold(1000, 1) is True)

        #dump tree and load tree
        tree_mgr.dump_tree_nodes("test_tree.csv")

        tree_mgr_load = TreeMgr()
        tree_mgr_load.load_tree_nodes("test_tree.csv")
        tree_node1 = tree_mgr_load.get_tree_node([1])
        #print(tree_mgr_load.root_tree_node.childNodes)
        print("node: node_id= {} height={}, index={}".format(tree_node1.node_id, tree_node1.height, tree_node1.index))
        self.assertEqual(tree_node1.node_id, "1")
        self.assertEqual(tree_node1.height, 1)
        self.assertEqual(tree_node1.index, 1)
        self.assertEqual(tree_node1.get_prop("total"), 1)

class TestFunction(unittest.TestCase):     

    def test_convert_location_1(self):
        i, j = convert_location(55, 11)
        print("test_convert_location_1 i,j",i, j)
        self.assertEqual(i, 0)
        self.assertEqual(j, 5)

        i, j = convert_location(73, 11)
        print("test_convert_location_1 i,j",i, j)
        self.assertEqual(i, 7)
        self.assertEqual(j, 6)

        i, j = convert_location(46, 11)
        print("test_convert_location_1 i,j",i, j)
        self.assertEqual(i, 2)
        self.assertEqual(j, 4)

if __name__ == '__main__':
    function.init_log()
    unittest.main()