class nodeMap:
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
        return len(list(filter(
            lambda x: x['server_ip'] == server_ip and x['server_port'] == server_port, self.map))) > 0

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
            res.append({'server_ip': node['server_ip'], 'server_port': node['server_port']})
        return res

    def get_all_nodes(self):
        return self.map
