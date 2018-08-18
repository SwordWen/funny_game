

class NetNode:
    def __init__(self, layer = None, index = None):
        self.node_id = str(layer) + "," + str(index)
        self.layer = layer
        self.index = index
        self.ingressNodes = {}
        self.egressNodes = {}
        self.properties = {}

    def get_prop(self, key):
        if key in self.properties.keys():
            return self.properties[key]
        else:
            return ""
    
    def set_prop(self, key, value):
        self.properties[key] = value

    def inc_prop(self, key, value):
        if key not in self.properties.keys():
            self.properties[key] = int(value)
        else:
            self.properties[key] += int(value)

class NetMgr:
    def __init__(self):
        self.net_layer = []

    def update_net_nodes(self, steps=[], result=0):

        for i in range(len(steps)):
            if steps[i] < 0:
                break

            if i >= len(self.net_layer):
                self.net_layer.append({})

            if steps[i] not in self.net_layer[i]:
                self.net_layer[i][steps[i]] = NetNode(i, steps[i])

            net_node = self.net_layer[i][steps[i]]
            net_node.inc_prop("total", 1)
            if result == 10:
                net_node.inc_prop("success", 1)
            elif result == 0:
                net_node.inc_prop("failure", 1)
            elif result == 5:
                net_node.inc_prop("draw", 1)
                
    def get_net_node(self, steps=[]):

        net_node = None
        steps_num = len(steps)

        if steps_num <= len(self.net_layer):
            if steps[-1] in self.net_layer[steps_num-1]:
                return self.net_layer[steps_num-1][steps[-1]]
        return net_node
        

