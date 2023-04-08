from .helper import module
from scapy.plist import PacketList
class CoreStructure:
    '''
    This is the root of all class where the core
    dictionary is stored
    '''
    _core_dict = dict()
    # _packets = None

    def __init__(self):
        '''
        It expects a scapy parsed dump file
        '''
        self._core_dict = {}
        # self._packets = scapy_packets

    def start(self, packet):
        '''
        This function begins the actual analysis of scapy parsed file
        '''
        s_socket, d_socket = (None, None)
        try:
            s_socket, d_socket = module.extract_socket(packet)
        except:
            print(f'Error:{packet}')
        if not s_socket or not d_socket:
            return
                # print('Ughh.. Problem')
                # print(module.debug_packet(packet))
        else:
            try:
                if not (s_socket, d_socket) in self._core_dict:
                    if not (d_socket, s_socket) in self._core_dict:
                            # The connection doesn't exist create a new one
                        self._core_dict[(s_socket, d_socket)] = module.create_connection(packet)
                    else:
                            # The connection does exist just set the swap=true
                        self._core_dict[(d_socket, s_socket)].update(packet, swap=True)
                else:
                    self._core_dict[(s_socket, d_socket)].update(packet)
            except:
                return
    
    def serialize(self, analyze: dict, problem_ips: list):
        hosts = set()
        serialized_dict = {
            'tcp': [],
            'udp': [],
            'icmp': [],
            'dns': [],
            'invalid': [],
            'analyze': {
                'counts': {
                    'tcp_downloaded': 0,
                    'tcp_uploaded': 0,
                    'udp_downloaded': 0,
                    'udp_uploaded': 0,
                    'threats': 0,
                    'tcp_con': 0,
                    'udp_con': 0,
                },
                'tcp': [],
                'udp': [],
                'dns': [],
                'icmp': [],
                'invalid': [],
            },
            "edges": [],
            "hosts": []
        }

        for edge, connection in zip(self._core_dict.keys(), self._core_dict.values()):
            source, destination = edge
            #provision for ipv6
            ip_port= source.split(":")
            source_port=ip_port[-1]
            source_ip=ip_port[:-2]
            if len(source_ip)>1:
                #ipv6
                source_ip=":".join(source_ip)
            else:
                #ipv4
                source_ip="".join(source_ip)
            
            ip_port= destination.split(":")
            destination_port=ip_port[-1]
            destination_ip=ip_port[:-2]
            if len(destination_ip)>1:
                #ipv6
                destination_ip=":".join(destination_ip)
            else:
                #ipv4
                destination_ip="".join(destination_ip)
                
            
            _edge = {
                "source_ip": source_ip,
                "source_port": source_port,
                "destination_ip": destination_ip,
                "destination_port": destination_port
            }
            connection_serialized_dict = connection.serialize()
            if 'ip' in connection_serialized_dict:
                connection_serialized_dict['invisible'] = compare_ips(problem_ips, connection_serialized_dict['ip'])

            if 'type' in connection_serialized_dict:
                connection_serialized_dict.pop('type', None)
                serialized_dict['dns'].append(connection_serialized_dict)
                _edge["type"] = "DNS"
                _edge["data"] = {
                    "requested_domain": connection_serialized_dict["requested_domain"],
                    "response_ip": connection_serialized_dict["response_ip"]
                }
            elif isinstance(connection, module.TCPSegment):
                serialized_dict['tcp'].append(connection_serialized_dict)
                _edge["type"] = "TCP"
                _edge["data"] = {
                    "upload": connection_serialized_dict["upload"],
                    "download": connection_serialized_dict["download"],
                    "protocol": connection_serialized_dict["protocol"]
                }
            elif isinstance(connection, module.ICMP):
                serialized_dict['icmp'].append(connection_serialized_dict)
                _edge["type"] = "ICMP"
                _edge["data"] = {
                    "average_ping": connection_serialized_dict["average_ping"],
                    "total_requests": connection_serialized_dict["total_requests"],
                }
            elif isinstance(connection, module.Invalid):
                serialized_dict['invalid'].append(connection_serialized_dict)
                _edge["type"] = "INVALID"
                _edge["data"] = {
                }
            elif isinstance(connection, module.UDPDatagram):
                serialized_dict['udp'].append(connection_serialized_dict)
                _edge["type"] = "UDP"
                _edge["data"] = {
                    "upload": connection_serialized_dict["upload"],
                    "download": connection_serialized_dict["download"],
                    "protocol": connection_serialized_dict["protocol"]
                }
            serialized_dict['edges'].append(_edge)
            hosts.add(source_ip)
            hosts.add(destination_ip)
        
        serialized_dict['hosts'] = list(hosts)

        for agg_con in analyze.values():
            if agg_con['type'] == 'TCP':
                serialized_dict['analyze']['counts']['tcp_downloaded'] += agg_con['downloaded']
                serialized_dict['analyze']['counts']['tcp_uploaded'] += agg_con['uploaded']
                serialized_dict['analyze']['counts']['threats'] += 1 if agg_con['is_dos'] or agg_con['is_nmap'] else 0
                serialized_dict['analyze']['counts']['tcp_con'] += 1
            if agg_con['type'] == 'UDP':
                serialized_dict['analyze']['counts']['udp_downloaded'] += agg_con['downloaded']
                serialized_dict['analyze']['counts']['udp_uploaded'] += agg_con['uploaded']
                serialized_dict['analyze']['counts']['threats'] += 1 if agg_con['is_dos'] else 0
                serialized_dict['analyze']['counts']['udp_con'] += 1
            if agg_con['type'] != 'DNS':
                s_addr, d_addr = agg_con['s/d']
                agg_con.pop('s/d', None)
                agg_con['source_address'] = s_addr
                agg_con['destination_address'] = d_addr
            serialized_dict['analyze'][agg_con['type'].lower()].append(agg_con)

        return serialized_dict

    def __str__(self):
        return self._core_dict.__str__()

def compare_ips(problem_ips, current_ip):
    s_c_ip = current_ip['source_address']
    d_c_ip = current_ip['destination_address']
    for s_p_ip, d_p_ip in problem_ips:
       if s_c_ip == s_p_ip and d_c_ip == d_p_ip:
           return True
    return False