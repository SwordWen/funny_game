
"""

steps_history:
| index     | steps                           | flag   | winner| record_time  | key_value               |
| hash code | [8, 4, 5, 7, 2, 3, 6, 1, 0]     |   0    |       | 2018-5-9     | key1=value1;key2=value2 |

board layout: 
0 1 2
3 4 5
6 7 8
steps sequence: 
[8, 4, 5, 7, 2, 3, 6, 1, 0] 

1. sqlite:
CREATE TABLE steps_history (index varchar(10), steps varchar(32), flag int, winner int, record_time varchar(32), key_value text)

2. cql:
CREATE KEYSPACE games
  WITH REPLICATION = { 
   'class' : 'SimpleStrategy', 
   'replication_factor' : 1 
  };

CREATE TABLE games.steps_history ( 
   id text PRIMARY KEY, 
   steps text, 
   flag int,
   winner int,
   record_time text,
   key_value text
    );
"""

import os
import sqlite3
import logging
import ast
import argparse
import sys
import hashlib
import time
import uuid
from collections import deque


##
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

########################

def hash_function(input_str):
    return hashlib.sha1(input_str).hexdigest()

#convert
def str_to_dict(str):
    pass

def dict_to_str(key_value={}):
    kv_str = ""
    for k in key_value.keys():
        kv_str = "{0}={1},".format(k,key_value[k])
    
    return kv_str.strip(",")

def time_to_str(secs=None):
    "Exapmle: 2017-12-02 08:05:39 UTC"
    return time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(secs))

######################
class TreeNode:
    def __init__(self, parent = None, height = None, index = None):
        # make a random UUID
        #self.node_id = uuid.uuid4()
        self.parentNode = parent # "None" for the root node
        self.height = height
        self.index = index
        self.childNodes = {}
        self.properties = {}

    def get_prop(self, key):
        if key in self.properties.keys():
            return self.properties[key]
    
    def set_prop(self, key, value):
        self.properties[key] = value

    def set_or_add_prop(self, key, value):
        if key not in self.properties.keys():
            self.properties[key] = value
        else:
            self.properties[key] += value

    def add_child_if_not_existing(self, child_index):
        if child_index not in self.childNodes.keys():
            self.childNodes[child_index] = TreeNode(self, self.height + 1, child_index)
        else:
            logging.debug("add_child_if_not_existing: node with index({0}) is existing.".format(child_index))

    def get_or_add_child(self, child_index):
        if child_index not in self.childNodes.keys():
           self.childNodes[child_index] = TreeNode(self, self.height + 1, child_index)        
        return self.childNodes[child_index]

    def get_child(self, child_index):
        if child_index in self.childNodes.keys():
            return self.childNodes[child_index]
        else:
            return None

class GameHistory:
    """class to handle game history information"""
    def is_connected(self):
        pass

    def connect(self, database):
        pass

    def disconnect(self):
        pass

    def store_steps(self, board_size=3, steps=[], winner=0, kv={}):
        pass

class CassandraGameHistory:
    """class to handle game history information"""
    cluster = None
    session = None
    board_size = -1
    win_length = -1

    def is_connected(self):
        return self.session != None

    def connect(self, database, server_list=[]):
        keyspace = database
        auth_provider = PlainTextAuthProvider(username='cassandra', password='cassandra')
        self.cluster = Cluster(auth_provider=auth_provider, contact_points=server_list)
        self.session = self.cluster.connect(keyspace)

    def disconnect(self):
        pass

    def set_board_size(self, board_size=-1):
        self.board_size = board_size

    def set_win_length(self, win_length=-1):
        self.win_length = win_length

    def store_steps(self, steps=[], winner=0, kv={}):
        """
CREATE TABLE games.steps_history_11_5 ( 
   id text PRIMARY KEY, 
   steps text, 
   flag int,
   winner int,
   record_time text,
   key_value text
    );
"""
        table_name = "steps_history_{0}_{1}".format(self.board_size, self.win_length)
        if self.is_connected():
            steps_seq = str(steps)
            index = hash_function(steps_seq)
            now_time = time_to_str()
            kv_str = dict_to_str(kv)
            flag = 0
            self.session.execute(
                """
                INSERT INTO steps_history_11_5 (id, steps, flag, winner, record_time, key_value)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (index, steps_seq, flag, int(winner), now_time, kv_str)
            )  

class SqliteGameHistory:
    """class to handle game history information"""

    sqlite_conn = None
    root_tree_node = TreeNode(None, 0, 0)

    def is_connected(self):
        if self.sqlite_conn is None:
            return False
        else:
            return True

    def connect(self, database):
        """database: sqlite file"""
        data_file = database
        if os.path.isfile(data_file):
            logging.info("Connect sqlite {0}".format(data_file))
            self.sqlite_conn = sqlite3.connect(data_file)
        else:
            #if data_file is not existing, the connect will create one
            logging.info("Create sqlite {0}".format(data_file))
            self.sqlite_conn = sqlite3.connect(data_file)
            cur = self.sqlite_conn.cursor()
            sql = "CREATE TABLE steps_history(index_id varchar(10), steps varchar(32), flag int, winner int, record_time varchar(32), key_value text);"
            cur.execute(sql)
            #commit db change
            self.sqlite_conn.commit()

    def disconnect(self):
        if self.sqlite_conn != None:
            self.sqlite_conn.close()
            self.sqlite_conn = None

    def record_is_existing(self, steps=[]):
        cur = self.sqlite_conn.cursor()
        steps_seq = str(steps)
        index = hash_function(steps_seq)
        cur.execute('select index_id from steps_history where index_id=?', (index, ))
        index_record = cur.fetchone()
        #logging.debug("user_is_existing: {0}".format(user))
        if index_record is None:
            return False
        else:
            return True

    def store_steps(self, steps=[], winner=0, kv={}):
        steps_seq = str(steps)
        index = hash_function(steps_seq)

        if self.record_is_existing(steps) == False:
            now_time = time_to_str()
            kv_str = dict_to_str(kv)
            flag = 0
            cur = self.sqlite_conn.cursor()
            cur.execute("insert into steps_history(index_id, steps, flag, winner,  record_time,  key_value) values (?, ?, ?, ?, ?, ?)"
                , (index.strip(), steps_seq.strip(), flag, winner,  now_time.strip(), kv_str))
            #commit data change
            self.sqlite_conn.commit()
            #logging.debug("[{0}] steps is stored.".format(index))


    ##############################################
    def get_record_by_steps(self, steps=[]):
        pass

    def update_tree_nodes(self, steps=[], result=0):
        parent = self.root_tree_node
        for step in steps:
            child = parent.get_or_add_child(step)
            child.set_or_add_prop("total", 1)
            #Todo
            if result == 10:
                child.set_or_add_prop("success", 1)
            elif result == 0:
                child.set_or_add_prop("failure", 1)
            parent = child

    def get_tree_node(self, steps=[]):
        parent = self.root_tree_node
        step_node_map = {}
        for step in steps:
            child = parent.get_child(step)
            step_node_map[step] = child
        return step_node_map
            


    def dump_tree_nodes(self):
        parent = self.root_tree_node

        queue = deque()
        for key, child in parent.childNodes.iteritems():
            queue.append(child)
            print("visit node: parent_index= {} height={}, index={}".format(parent.index, child.height, child.index))

        while(len(queue) > 0):        
            visit_node = queue.popleft()
            for key, child in visit_node.childNodes.iteritems():
                queue.append(child)
                print("visit node: parent_index= {} height={}, index={}".format(visit_node.index, child.height, child.index))
        

    
    def load_tree_nodes(self):
        pass

    def select_steps_from_history(self, count=10):
        cur = self.sqlite_conn.cursor()
        for row in cur.execute('select steps, winner from steps_history LIMIT 10'):
            print row

        
    def build_policy_tree_from_history(self, flag=0):
        while True:
            cur = self.sqlite_conn.cursor()
            cur.execute("update top (100) steps_history set flag = 1 where flag = 0")
            self.sqlite_conn.commit()
            for row in cur.execute('select steps, winner from steps_history where flag=1'):
                print row

            


