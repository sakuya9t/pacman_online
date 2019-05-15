# COMP90020 Distributed Algorithms project
# Author: Zijian Wang 950618, Nai Wang 927209, Leewei Kuo 932975, Ivan Chee 736901

class nodeMap:
    """
    a class that contains all the information of the nodes in the current P2P connection
    """
    def __init__(self):
        self.map = []

    def __str__(self):
        return str(self.map)

    def append(self, ip, port, server_ip, server_port, role, status):
        self.map.append({'ip': ip, 'port': port, 'server_ip': server_ip,
                         'server_port': server_port, 'agent': role, 'status': status})

    def exists(self, ip, port, server_ip, server_port):
        return len(list(filter(lambda x: x['ip'] == ip and x['port'] == port
                               and x['server_ip'] == server_ip and x['server_port'] == server_port,
                               self.map))) > 0

    def exists_server(self, server_ip, server_port):
        for node in self.map:
            if node['server_ip'].__eq__(server_ip) and node['server_port'] == server_port:
                return True
        return False

    def exists_agent(self, agent):
        return len(list(filter(lambda x: x['agent'] == agent, self.map))) > 0

    def update(self, ip, port, server_ip, server_port, role, status):
        self.remove(ip, port)
        self.append(ip, port, server_ip, server_port, role, status)

    def remove(self, ip, port):
        nodes = list(filter(
            lambda x: (x['ip'] == ip and x['port'] == port), self.map))
        for node in nodes:
            try:
                self.map.remove(node)
            except:
                continue

    def get_all_servers(self):
        res = []
        for node in self.map:
            res.append({'server_ip': node['server_ip'], 'server_port': node['server_port'],
                        'agent_id': node['agent']})
        return res

    def get_all_nodes(self):
        return self.map

    def get_all_roles(self):
        roles = []
        for node in self.map:
            roles.append(node['agent'])
        return roles

    def get_role(self, ip, port):
        for node in self.map:
            if node['ip'] == ip and node['port'] == port:
                return node['agent']

    # return the (ip, port) list of nodes that have a higher id than my_node
    def get_election_nodes(self, my_node):
        higher_id_node = []
        for node in self.map:
            node_id = node['agent']
            if node_id > my_node:
                ip, port = node['ip'], node['port']
                higher_id_node.append((ip, port))
        return higher_id_node

    # get how many nodes are connected to current node.
    def size(self):
        return len(self.map)
