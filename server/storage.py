"""
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
import csv
import ast
from collections import deque
from function import init_log

##
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
##
from function import parse_args
##
from tree import TreeMgr

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

def convert_location(index, board_size):
    i = index % board_size 
    j = (index - i) / board_size
    return i, j

######################
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
        self.cluster = Cluster(auth_provider=auth_provider, contact_points=server_list, 
            connect_timeout = 30)
        self.session = self.cluster.connect(keyspace)
        self.session.default_timeout = 30.0

    def disconnect(self):
        pass

    def set_board_size(self, board_size=-1):
        self.board_size = board_size

    def set_win_length(self, win_length=-1):
        self.win_length = win_length

    def store_steps(self, steps=[], winner=0, kv={}):
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
  
    def select_steps_from_history(self, handle_flag=0, count=10):
        cur = self.sqlite_conn.cursor()
        for row in cur.execute('select steps, winner from steps_history LIMIT 10'):
            print(row)  


"""
UPDATE steps_history_11_5 SET flag = %s WHERE flag != %s IF EXISTS;
"""
def select_steps_from_history(history_storage, tree_mgr,  handle_flag=0, count=10):
    table_name = "steps_history_{0}_{1}".format(history_storage.board_size, history_storage.win_length)
    if history_storage.is_connected():
        #update record for handling
        select_cmd = "SELECT id, steps, flag, winner FROM {0} where flag = {1} LIMIT {2} ALLOW FILTERING;".format(table_name, 0, count)
        #print("select_steps_from_history : " + select_cmd)
        rows = history_storage.session.execute(select_cmd)
        for row in rows:
            #print row.id, row.flag, row.steps, row.winner
            update_cmd = "UPDATE {0} SET flag = {1} WHERE id = '{2}' IF EXISTS;".format(table_name, 0-handle_flag, row.id)
            history_storage.session.execute(update_cmd) 
  
        #update record if handled
        select_cmd = "SELECT id, steps, flag, winner FROM {0} where flag = {1} LIMIT {2} ALLOW FILTERING;".format(table_name, 0-handle_flag, count)
        rows = history_storage.session.execute(select_cmd)
        #update policy tree 
        for row in rows:
            tree_mgr.update_tree_nodes(ast.literal_eval(row.steps), int(row.winner))
            update_cmd = "UPDATE {0} SET flag = {1} WHERE id = '{2}' IF EXISTS;".format(table_name, handle_flag, row.id)
            history_storage.session.execute(update_cmd)  

def build_policy_tree_from_history(history_storage, tree_mgr, handle_flag=0, max_count=1000):
    batch_count = 100
    loop_count = int(max_count/batch_count)
    for i in range(loop_count):
        select_steps_from_history(history_storage, tree_mgr, handle_flag, batch_count)

def main():
    init_log()
    args = parse_args()

    count = 1000
    server_list = ["127.0.0.1"]
    file_name = "default_policy_tree.csv"


    if args.file != None:
        file_name = args.file
    else:
        logging.info("Will use default file: " + file_name)

    if args.build == True:
        if args.flag != None:
            handle_flag = int(args.flag)
        else:
            print("Must set flag")
            return 

        if args.count != None:
            count = int(args.count)
        if args.addr != None:
            server_list = str(args.addr).split(",")
        borad_size = 11
        win_length = 5
        db_type = "cassandra"

        game_history = CassandraGameHistory()
        game_history.set_board_size(borad_size)
        game_history.set_win_length(win_length)
        game_history.connect("games", server_list)

        tree_mgr = TreeMgr()
        build_policy_tree_from_history(game_history, tree_mgr, handle_flag, count)
        tree_mgr.dump_tree_nodes(file_name, 1)

        game_history.disconnect()
    
    if args.load == True:
        tree_mgr = TreeMgr()
        tree_mgr.load_tree_nodes(file_name)
        tree_mgr.stat_tree_nodes()

    if args.filter == True:
        new_file = file_name.replace(".csv", "_new.csv")
        if args.newfile != None:
            new_file = args.newfile
        tree_mgr = TreeMgr()
        tree_mgr.load_tree_nodes(file_name)
        tree_mgr.stat_tree_nodes()
        tree_mgr.dump_tree_nodes(new_file, 1)

#python storage.py --build --addr 127.0.0.1 --flag 1 --file tree1.csv --count 100000
#python storage.py --load --file data/tree2_filter.csv
#python storage.py --filter --newfile filter_tree.csv
if __name__ == "__main__":
    """ Play a single game to the end using UCT for both players. 
    """
    main()



