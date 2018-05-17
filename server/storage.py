
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


CREATE TABLE steps_history (index varchar(10), steps varchar(32), flag int, winner int, record_time varchar(32), key_value text)

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
    def __init__(self, parent = None):
        # make a random UUID
        self.node_id = uuid.uuid4()
        self.parentNode = parent # "None" for the root node
        self.childNodes = {}
        self.properties = {}

    def getProp(key):
        if key in self.properties.keys():
            return self.properties[key]
    
    def setProp(key, value):
        self.properties[key] = value
        

class SqliteGameHistory:
    """class to handle user information"""

    sqlite_conn = None

    def is_connected(self):
        if self.sqlite_conn is None:
            return False
        else:
            return True

    def connect(self, data_file):
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
            logging.info("[{0}] steps is stored.".format(index))

    def get_record_by_steps(self, steps=[]):
        pass

    def build_policy_tree_from_history(self, flag=0):
        while True:
            cur = self.sqlite_conn.cursor()
            cur.execute("update top (100) steps_history set flag = 1 where flag = 0")
            self.sqlite_conn.commit()
            for row in cur.execute('select steps, winner from steps_history where flag=1'):
                print row

            


