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

class TreeNode:
    def __init__(self, parent = None, height = None, index = None):
        # make a random UUID
        #self.node_id = uuid.uuid4()
        self.parentNode = parent # "None" for the root node
        if parent is None:
            self.node_id = ""
        else:
            if "" == parent.node_id:
                self.node_id = str(index)
            else:
                self.node_id = parent.node_id + "," + str(index)

        self.height = height
        self.index = index
        self.childNodes = {}
        self.properties = {}
    
    def is_parent(self):
        return True if len(self.childNodes) > 0 else False

    def get_prop(self, key):
        if key in self.properties.keys():
            return self.properties[key]
        else:
            return ""
    
    def set_prop(self, key, value):
        self.properties[key] = value

    def inc_prop(self, key, value):
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
        index = int(child_index)
        if index not in self.childNodes.keys():
           self.childNodes[index] = TreeNode(self, self.height + 1, index)        
        return self.childNodes[index]

    def get_child(self, child_index):
        #print("get_child: node_id={0}, childNodes={1}".format(self.node_id, self.childNodes))
        if child_index in self.childNodes.keys():
            return self.childNodes[child_index]
        else:
            return None
    def above_threshold(self, rate, threshold):
        # logging.debug("above_threshold: height={}, index={}, success={} failure={} total={} children={}".
        #     format(self.height, self.index, self.get_prop("success"), self.get_prop("failure"), self.parentNode.get_prop("total"), len(self.childNodes)))
        if self.height %2 == 1 :
            if self.get_prop("success") != "" and len(self.childNodes) > 1  and int(self.get_prop("success"))*rate/int(self.parentNode.get_prop("total")) > threshold :
                return True
            else:
                return False
        else:
            if self.get_prop("failure") != "" and len(self.childNodes) > 1 and int(self.get_prop("failure"))*rate/int(self.parentNode.get_prop("total")) > threshold :
                return True
            else:
                return False
            
class TreeMgr:

    def __init__(self):
        self.root_tree_node = TreeNode(None, 0, 0)

    def update_tree_nodes(self, steps=[], result=0):
        parent = self.root_tree_node
        parent.inc_prop("total", 1)

        for step in steps:
            if step >= 0:
                child = parent.get_or_add_child(step)
                child.inc_prop("total", 1)
                #Todo
                if result == 10:
                    child.inc_prop("success", 1)
                elif result == 0:
                    child.inc_prop("failure", 1)
                elif result == 5:
                    child.inc_prop("draw", 1)
                parent = child
            else:
                break

    def get_tree_node(self, steps=[]):
        parent = self.root_tree_node
        #print("get_tree_node:" + str(steps))
        for step in steps:
            child = parent.get_child(step)  
        #print("get_tree_node:" + str(child))          
        return child

    def create_tree_node(self, steps=[]):
        parent = self.root_tree_node
        for step in steps:            
            child = parent.get_or_add_child(step)
            parent = child
        return child

    def get_all_tree_nodes(self, steps=[]):
        parent = self.root_tree_node
        step_node_map = {}
        for step in steps:
            child = parent.get_child(step)
            step_node_map[step] = child
        return step_node_map

    def calc_tree_length(self, parent_node = None):

        if parent_node is None:
            parent = self.root_tree_node
        else:
            parent = parent_node 

        tree_length = 0

        queue = deque()
        for key, child in parent.childNodes.iteritems():
            queue.append(child)
            if child.height > tree_length:
                tree_length = child.height

        while(len(queue) > 0):        
            visit_node = queue.popleft()
            for key, child in visit_node.childNodes.iteritems():
                queue.append(child)
                if child.height > tree_length:
                    tree_length = child.height

        return tree_length

    def calc_child_num(self, parent_node = None):
        child_num = 0 
        if parent_node is None:
            parent = self.root_tree_node
        else:
            parent = parent_node
        queue = deque()
        for key, child in parent.childNodes.iteritems():
            queue.append(child)
            if child.is_parent() is False:
                child_num += 1

        while(len(queue) > 0):        
            visit_node = queue.popleft()
            for key, child in visit_node.childNodes.iteritems():
                queue.append(child)
                if child.is_parent() is False:
                    child_num += 1
        return child_num

    def stat_tree_nodes(self, parent_node = None):

        parent = self.root_tree_node

        rate = 1000
        threshold = 1

        queue = deque()
        for key, child in parent.childNodes.iteritems():
            queue.append(child)
            #print("visit node: node_id= {} height={}, index={}".format(child.node_id, child.height, child.index))
            if child.above_threshold(rate, threshold):
                if child.height % 2 == 1:
                    logging.info("visit node: height={}, index={}, localcation, success={}".
                        format(child.height, child.index, child.get_prop("success")))
                else:
                    logging.info("visit node: height={}, index={}, failure={}".
                        format(child.height, child.index, child.get_prop("failure")))


        while(len(queue) > 0):        
            visit_node = queue.popleft()
            for key, child in visit_node.childNodes.iteritems():
                queue.append(child)
                #print("visit node: node_id= {} height={}, index={}".format(child.node_id, child.height, child.index))
                if child.above_threshold(rate, threshold):
                    if child.height % 2 == 1:
                        logging.info("visit node: height={}, index={}, success={}".
                            format(child.height, child.index, child.get_prop("success")))
                    else:
                        logging.info("visit node: height={}, index={}, failure={}".
                            format(child.height, child.index, child.get_prop("failure")))


    def dump_tree_nodes(self, file_name, threshold = 0, rate = 1000):
        with open(file_name, 'wb') as csvfile:
            logging.info("dump_tree_nodes: " + file_name)
            csvwriter = csv.writer(csvfile, delimiter=',')

            parent = self.root_tree_node
            csvwriter.writerow([parent.node_id, parent.height, parent.index, 
                parent.get_prop("total"), parent.get_prop("success"), parent.get_prop("failure"), parent.get_prop("draw")])

            queue = deque()
            for key, child in parent.childNodes.iteritems():
                queue.append(child)
                #print("visit node: node_id= {} height={}, index={}".format(child.node_id, child.height, child.index))
                if threshold > 0 and child.above_threshold(rate, threshold):
                    csvwriter.writerow([child.node_id, child.height, child.index, 
                        child.get_prop("total"), child.get_prop("success"), child.get_prop("failure"), child.get_prop("draw")])

            while(len(queue) > 0):        
                visit_node = queue.popleft()
                for key, child in visit_node.childNodes.iteritems():
                    queue.append(child)
                    #print("visit node: node_id= {} height={}, index={}".format(child.node_id, child.height, child.index))
                    if threshold > 0 and child.above_threshold(rate, threshold):
                        csvwriter.writerow([child.node_id, child.height, child.index, 
                            child.get_prop("total"), child.get_prop("success"), child.get_prop("failure"), child.get_prop("draw")])
        
    def load_tree_nodes(self, file_name):
        logging.info("load_tree_nodes: " + file_name)
        self.root_tree_node = TreeNode(None, 0, 0)

        with open(file_name, 'rb') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',')
            row = csvreader.next()
            self.root_tree_node.set_prop("total", int(row[3]))
            #print(row)
            for row in csvreader:
                #print(row)
                steps = str(row[0]).split(",")
                tree_node = self.create_tree_node(steps)
                if row[3].strip() != "":
                    tree_node.set_prop("total", int(row[3]))
                if row[4].strip() != "":
                    tree_node.set_prop("success", int(row[4]))
                if row[5].strip() != "":
                    tree_node.set_prop("failure", int(row[5]))
                if row[6].strip() != "":
                    tree_node.set_prop("draw", int(row[6]))

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



