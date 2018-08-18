##for all test modules
import unittest
import logging
import sys

#for test module

##for target module
sys.path.append("../")
import function 

from net import NetMgr

class TestNetMgr(unittest.TestCase):     

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
        # update net nodes
        net_mgr = NetMgr()
        net_mgr.update_net_nodes([1, 0, 2, 3, 7, 6, 8, 4, 5], 0)
        net_mgr.update_net_nodes([7, 5, 6, 3, 0, 1, 2, 4, 8], 0)
        net_mgr.update_net_nodes([4, 6, 3, 8, 2, 7, 1, 5, 0], 10)
        net_mgr.update_net_nodes([2, 5, 7, 0, 4, 3, 6, 1, 8], 10)
        net_mgr.update_net_nodes([3, 1, 7, 8, 0, 5, 4, 2, 6], 10)
        net_mgr.update_net_nodes([3, 5, 7, 0, 1, 2, 8, 6, 4], 10)

        net_node1 = net_mgr.get_net_node([1])
        self.assertEqual(net_node1.node_id, "0,1")
        self.assertEqual(net_node1.layer, 0)
        self.assertEqual(net_node1.index, 1)
        #self.assertEqual(tree_node1.get_prop("total"), 1)

if __name__ == '__main__':
    function.init_log()
    unittest.main()