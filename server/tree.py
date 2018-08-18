import logging

import csv
import ast
from collections import deque
from function import init_log

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
                if threshold <= 0 or child.above_threshold(rate, threshold):
                    csvwriter.writerow([child.node_id, child.height, child.index, 
                        child.get_prop("total"), child.get_prop("success"), child.get_prop("failure"), child.get_prop("draw")])

            while(len(queue) > 0):        
                visit_node = queue.popleft()
                for key, child in visit_node.childNodes.iteritems():
                    queue.append(child)
                    #print("visit node: node_id= {} height={}, index={}".format(child.node_id, child.height, child.index))
                    if threshold <= 0 or child.above_threshold(rate, threshold):
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
