import datetime
import json
import statistics
from dateutil import tz
from itertools import zip_longest
from .constants import known_protocols, dns_types, tcp_flags

def debug_packet(raw_packet):
    '''
    Print imp debug info from a packet
    '''
    return f'{raw_packet.name}, {raw_packet.src}->{raw_packet.dst}, {raw_packet.layers}'

def extract_socket(raw_packet) -> tuple:
    '''
    Retrieve socket addresses
    '''
    #TODO: Implement logic to extract identifier for proto other than TCP/UDP
    if raw_packet.getlayer(2) and raw_packet.getlayer(1).name.find('IP') == 0:
        s_ip = raw_packet.getlayer(1).src
        d_ip = raw_packet.getlayer(1).dst
        if raw_packet.getlayer(2).name == 'TCP' or raw_packet.getlayer(2).name == 'UDP':
            s_port = getattr(raw_packet.getlayer(2), 'sport')
            d_port = getattr(raw_packet.getlayer(2), 'dport')
            return (f'{s_ip}:{s_port}', f'{d_ip}:{d_port}')
        elif raw_packet.getlayer(2).name == 'ICMP':
            _id = getattr(raw_packet.getlayer(2), 'id')
            return (f'{s_ip}:{_id}', f'{d_ip}:{_id}')
    elif raw_packet.getlayer(0):
        s_adr = getattr(raw_packet.getlayer(0), 'src')
        d_adr = getattr(raw_packet.getlayer(0), 'dst')
        return (s_adr, d_adr)
    return (None, None)

def create_connection(raw_packet):
    '''
    Returns the appropriate instance of class that needs to be used
    Better to not clutter up the main loop
    '''
    if raw_packet.getlayer(1):
        # For now we are assuming IP cannot be on it's own
        if raw_packet.getlayer(2):
            if raw_packet.getlayer(2).name == 'ICMP':
                return ICMP(raw_packet)
            elif raw_packet.getlayer(2).name == 'TCP':
                return TCPSegment(raw_packet)
            elif raw_packet.getlayer(2).name == 'UDP':
                return UDPDatagram(raw_packet)
            else:
                return Invalid(raw_packet)
        else:
            return Invalid(raw_packet)
    else:
        # Packet with no IP layer? Ughh will think about this later!
        return Invalid(raw_packet)

def get_date(timestamp):
    if not timestamp or timestamp == 0:
        return ''
    from_zone = tz.gettz('UTC')
    to_zone = tz.tzlocal()

    utc_time = datetime.datetime.utcfromtimestamp(timestamp)
    utc_time = utc_time.replace(tzinfo=from_zone)
    central = utc_time.astimezone(to_zone)
    date = central.strftime('%d/%m/%Y, %H:%M:%S')
    return date

class Invalid:
    '''
    Anything that we don't know what to do with goes to this
    '''
    raw_bytes = None
    l2_proto = None
    l3_proto = None

    def __init__(self, raw_data):
        self.raw_bytes = str(raw_data)
        self.l2_proto = raw_data.getlayer(0).name if raw_data.getlayer(0) else 'UNKNOWN'
        self.l3_proto = raw_data.getlayer(1).name if raw_data.getlayer(1) else 'UNKWOWN'

    def update(self, raw_data, swap=True):
        return

    def serialize(self) -> dict:
        return {
            'layer2_protocol': self.l2_proto,
            'layer3_protocol': self.l3_proto,
        }

    def __str__(self):
        return f'UNKWOWN/INVALID: {self.l2_proto}, {self.l3_proto}'

# For now support only for Ping (reply/response) and Port Unreachable
class ICMP:
    '''
    To store ICMP packets
    '''
    ip_packet = None
    _id = None
    response_timestamps = dict() # [Reply received?, Request Sent timestamp, Response Received timestamp, Difference, No. of retries]
    _type = None

    def __init__(self, raw_data):
        self.ip_packet = IPPacket(raw_data)
        self.response_timestamps = dict()
        icmp_packet = raw_data.getlayer(2)
        self._id = getattr(icmp_packet, 'id')
        self._type = 'PING' if getattr(icmp_packet, 'type') == 8 else 'PORT UNREACHABLE'
        acknowledged = False if getattr(icmp_packet, 'type') == 8 else True
        self.response_timestamps[getattr(icmp_packet, 'seq')] = [acknowledged, float(raw_data.time), 0.0, 0.0, 0]

    def update(self, raw_data, swap=False):
        icmp_packet = raw_data.getlayer(1)
        seq_id = getattr(icmp_packet, 'seq')
        if swap:
            self.response_timestamps[seq_id][2] = float(raw_data.time)
            self.response_timestamps[seq_id][3] = float(raw_data.time) - self.response_timestamps[seq_id][1]
            self.response_timestamps[seq_id][0] = True
        else:
            if seq_id in self.response_timestamps:
                # ICMP request resent
                self.response_timestamps[seq_id][4] += 1
            else:
                # New request
                self.response_timestamps[seq_id] = [False, float(raw_data.time), 0.0, 0.0, 0]

    def serialize(self) -> dict:
        return {
            'ip': self.ip_packet.serialize(),
            'packet_type': self._type,
            'id': self._id,
            'total_requests': self.count_packets(),
            'responded_requests': self.count_packets() - self.count_failed(),
            'start_time': get_date(self.response_timestamps[1][1]) if 1 in self.response_timestamps else '',
            'average_ping': self.avg_response_time(),
        }

    def avg_response_time(self):
        avg_res = 0.0
        for key in self.response_timestamps:
            query = self.response_timestamps[key]
            if query[4] > 0:
                continue
            avg_res += query[3]
        avg_res = avg_res / len(self.response_timestamps)
        return datetime.datetime.utcfromtimestamp(avg_res).microsecond/1000

    def count_retries(self):
        retries = 0
        for key in self.response_timestamps:
            query = self.response_timestamps[key]
            retries += query[4]
        return retries

    def count_failed(self):
        failed = 0
        for key in self.response_timestamps:
            query = self.response_timestamps[key]
            if not query[0]:
                failed += 1
        return failed

    def count_packets(self):
        return len(self.response_timestamps)

    def __str__(self):
        return f'{self.ip_packet}, ICMP {self._type}, No. of req/res:{len(self.response_timestamps)}, Avg:{self.avg_response_time()}ms, Retries:{self.count_retries()}, Failed:{self.count_failed()}'

class IPPacket:
    '''
    To represent IP info
    '''
    s_ip_addr = ''
    d_ip_addr = ''
    protocol = ''

    def __init__(self, raw_data):
        self.s_ip_addr = raw_data.getlayer(1).src
        self.d_ip_addr = raw_data.getlayer(1).dst
        if len(self.s_ip_addr.split('.')) == 4:
            self.protocol = 'IPv4'
        else:
            self.protocol = 'IPv6'

    def serialize(self) -> dict:
        return {
            'source_address': self.s_ip_addr,
            'destination_address': self.d_ip_addr,
            'version': self.protocol
        }

    def __str__(self):
        return f'{self.s_ip_addr}->{self.d_ip_addr}, {self.protocol}'

class TCPSegment:
    '''
    Store TCP segment info
    '''
    s_port = ''
    d_port = ''
    ip_packet = None
    data_downloaded = 0 # Download and upload in the context of client
    data_uploaded = 0
    client_ack = None # From the pov of client
    server_ack = None
    app_layer = None
    protocol = ''
    fwd_packets = []
    bkwd_packets = []
    bkwd_segments = []
    init_win_bytes_forward = 0.0
    init_win_bytes_backward = 0.0
    connection_finished = False
    reception_timestamps = []
    transmission_timestamps = []
    unintended_connection = False
    min_length = 0.0
    flags=[]

    def __init__(self, raw_data):
        self.reception_timestamps = []
        self.transmission_timestamps = []
        self.s_port = getattr(raw_data, 'sport')
        self.d_port = getattr(raw_data, 'dport')
        self.app_layer = None
        self.ip_packet = IPPacket(raw_data)
        self.protocol = known_protocols[self.d_port] if (self.d_port) in known_protocols else 'UNKNOWN'
        self.min_length = 0.0
        # Necessary because many times the DNS data is simply not provided
        if 'DNS' in raw_data:
            self.app_layer = DNS(raw_data) if self.d_port == 53 else None
        self.fwd_packets = [len(raw_data)]
        self.bkwd_packets = []
        self.bkwd_segments = []
        self.init_win_bytes_backward = 0.0
        self.init_win_bytes_forward = len(raw_data['TCP'].payload)
        self.transmission_timestamps.append(float(raw_data.time))
        self.flags=[]
        self.flags.append(raw_data['TCP'].flags)

    def count_flags(self):
        counts = [0] * 8
        for flag in self.flags:
            counts[0] += 1 if flag & tcp_flags['FIN'] else 0
            counts[1] += 1 if flag & tcp_flags['SYN'] else 0
            counts[2] += 1 if flag & tcp_flags['RST'] else 0
            counts[3] += 1 if flag & tcp_flags['PSH'] else 0
            counts[4] += 1 if flag & tcp_flags['ACK'] else 0
            counts[5] += 1 if flag & tcp_flags['URG'] else 0
            counts[6] += 1 if flag & tcp_flags['ECE'] else 0
            counts[7] += 1 if flag & tcp_flags['CWR'] else 0
        return counts

    def get_time(self):
        flow_time = []

        for i in range(1, len(self.reception_timestamps), 2):
            flow_time.append(self.reception_timestamps[i] - self.reception_timestamps[i - 1])

        return flow_time

    def update(self, raw_data, swap=False):
        # This implementation should be good enough for now
        # Download/upload seems to be updating as intended
        # We are also counting the magic byte, but it shouldn't affect anything drastically

        # Ack from server = Data uploaded (from client POV)
        # Ack from client = Data downloaded (from client POV)
        flags = raw_data['TCP'].flags # Correct way to get flags
        #print(raw_data['TCP'].flags)
        #raw_data['TCP'].sprintf("%TCP.flags%")
        self.flags.append(flags)
        self.min_length = min(self.min_length, len(raw_data))
        if flags & tcp_flags['FIN'] or flags & tcp_flags['RST']:
            # If the connection is Resetted or Finished we will no longer update the download/upload
            self.connection_finished = True 
            if not self.server_ack:
                self.unintended_connection = True
            return

        if (self.d_port == 53 and not self.app_layer) and 'DNS' in raw_data:
            self.app_layer = DNS(raw_data)
            return

        if self.app_layer and 'DNS' in raw_data:
            self.app_layer.update(raw_data, swap)
        else:
            if not self.connection_finished:
                if swap:
                    # Here the segment is coming from the server
                    if len(self.bkwd_packets) == 0:
                        self.init_win_bytes_backward = len(raw_data['TCP'].payload)
                    self.bkwd_packets.append(len(raw_data))
                    self.bkwd_segments.append(len(raw_data['TCP']))
                    self.reception_timestamps.append(float(raw_data.time))
                    if not self.server_ack:
                        self.server_ack = getattr(raw_data, 'ack')
                    self.data_uploaded += getattr(raw_data, 'ack') - self.server_ack
                    self.server_ack = getattr(raw_data, 'ack')
                else:
                    self.fwd_packets.append(len(raw_data))
                    self.fwd_packets += 1
                    self.transmission_timestamps.append(float(raw_data.time))
                    if not self.client_ack:
                        self.client_ack = getattr(raw_data, 'ack')
                    self.data_downloaded += getattr(raw_data, 'ack') - self.client_ack
                    self.client_ack = getattr(raw_data, 'ack')

    def get_flow_time(self):
        return self.reception_timestamps[-1] - self.reception_timestamps[0] if len(self.reception_timestamps) > 0 else 0

    def serialize(self) -> dict:
        if self.app_layer:
            return self.app_layer.serialize('TCP', self.ip_packet)
        r_avg, t_avg = self.get_average_timestamps()
        counts = self.count_flags()
        bkwd_packets_len_std = statistics.pstdev(self.bkwd_packets) if len(self.bkwd_packets) else 0
        flow_time = self.get_time()
        return {
            'ip': self.ip_packet.serialize(),
            's_port': self.s_port,
            'd_port': self.d_port,
            'download': self.data_downloaded,
            'upload': self.data_uploaded,
            'protocol': self.protocol,
            'Init_Win_bytes_forward': self.init_win_bytes_forward,
            'Init_Win_bytes_backward': self.init_win_bytes_backward,
            'Min_Packet_Length': self.min_length,
            'Down_Up_Ratio': self.data_downloaded / (self.data_uploaded if self.data_uploaded > 0 else 1),
            'start_time': get_date(self.transmission_timestamps[0]) if len(self.transmission_timestamps) > 0 else '',
            'avg_rec_time': r_avg,
            'avg_trans_time': t_avg,
            'unintended': self.unintended_connection,
            'connection_finished': self.connection_finished,
            'flow_duration': self.reception_timestamps[-1] - self.reception_timestamps[0] if len(self.reception_timestamps) > 0 else 0,
            'fwd_packets': len(self.fwd_packets),
            'bkwd_packets': len(self.bkwd_packets),
            'fwd_packets_len_total': sum(self.fwd_packets),
            'bkwd_packets_len_total': sum(self.bkwd_packets),
            'fwd_packets_len_mean': sum(self.fwd_packets) / len(self.fwd_packets) if len(self.fwd_packets) > 0 else 1,
            'bkwd_packets_len_mean': sum(self.bkwd_packets) / len(self.bkwd_packets) if len(self.bkwd_packets) > 0 else 1,
            'fwd_packets_len_max': max(self.fwd_packets, default=0),
            'bkwd_packets_len_max': max(self.bkwd_packets, default=0),
            'fwd_packets_len_min': min(self.fwd_packets, default=0),
            'bkwd_packets_len_mix': min(self.bkwd_packets, default=0),
            'bkwd_packets_len_std': bkwd_packets_len_std,
            'Avg_bkwd_segment_size': statistics.mean(self.bkwd_segments) if len(self.bkwd_segments) else 0,
            'flow_IAT_mean': statistics.mean(flow_time) if len(flow_time) else 0,
            'flow_IAT_std': statistics.pstdev(flow_time) if len(flow_time) else 0,
            'flow_IAT_max': max(flow_time, default=0),
            'FIN_Flag_Count': int(counts[0] == (len(self.fwd_packets) + len(self.bkwd_packets))),
            'SYN_Flag_Count': int(counts[1] == (len(self.fwd_packets) + len(self.bkwd_packets))), 
            'RST_Flag_Count': int(counts[2] == (len(self.fwd_packets) + len(self.bkwd_packets))), 
            'PSH_Flag_Count': int(counts[3] == (len(self.fwd_packets) + len(self.bkwd_packets))), 
            'ACK_Flag_Count': int(counts[4] == (len(self.fwd_packets) + len(self.bkwd_packets))),
            'URG_Flag_Count': int(counts[5] == (len(self.fwd_packets) + len(self.bkwd_packets))),
            'ECE_Flag_Count': int(counts[6] == (len(self.fwd_packets) + len(self.bkwd_packets))),
            'CWE_Flag_Count': int(counts[7] == (len(self.fwd_packets) + len(self.bkwd_packets))), 
            #'flags': self.flags,
        }

    def get_average_timestamps(self) -> tuple:
        r_avg, t_avg = (0.0, 0.0)
        for r_time, t_time in zip_longest(self.reception_timestamps, self.transmission_timestamps):
            r_avg += r_time if r_time else 0
            t_avg += t_time if t_time else 0
        r_avg = r_avg / len(self.reception_timestamps) if len(self.reception_timestamps) != 0 else -1
        t_avg = t_avg / len(self.transmission_timestamps) if len(self.transmission_timestamps) != 0 else -1
        r_avg = datetime.datetime.utcfromtimestamp(r_avg).microsecond/1000
        t_avg = datetime.datetime.utcfromtimestamp(t_avg).microsecond/1000
        return (r_avg, t_avg)

    def is_unintended(self) -> str:
        return 'Unintended' if self.unintended_connection else ''
    
    def get_download(self) -> int:
        return self.data_downloaded

    def get_upload(self) -> int:
        return self.data_uploaded
    
    def print_dns(self) -> str:
        return self.app_layer if self.app_layer else ''

    def is_dns(self) -> bool:
        return True if self.app_layer else False

    def __str__(self):
        r_avg, t_avg = self.get_average_timestamps()
        return f'{self.ip_packet}, {self.s_port}->{self.d_port}, TCP:{self.protocol}, {self.print_dns()} Download: {self.data_downloaded}, Upload: {self.data_uploaded}, {self.is_unintended()} Avg Rec/Tra gap: {r_avg}/{t_avg}ms'

    def get_flags(self):
        return self.flags

class UDPDatagram:
    '''
    Store UDP Datagram info
    '''
    s_port = ''
    d_port = ''
    ip_packet = None
    protocol = ''
    downloaded = 0
    uploaded = 0
    reception_timestamps = []
    transmission_timestamps = []
    app_layer = None
    flags=[]

    def __init__(self, raw_data):
        self.ip_packet = IPPacket(raw_data)
        self.s_port = getattr(raw_data, 'sport')
        self.d_port = getattr(raw_data, 'dport')
        self.downloaded, self.uploaded = (0, 0)
        self.reception_timestamps = []
        self.transmission_timestamps = []
        self.protocol = known_protocols[self.d_port] if (self.d_port) in known_protocols else 'UNKNOWN'
        if self.d_port == 53:
            self.app_layer = DNS(raw_data)
        else:
            self.transmission_timestamps.append(float(raw_data.time))
        self.flags=[]
        self.flags.append(raw_data['UDP'].flags)

    def update(self, raw_data, swap=False):
        if self.app_layer:
            self.app_layer.update(raw_data, swap=swap)
        else:
            udp_data = raw_data['UDP']
            if swap:
                self.reception_timestamps.append(float(raw_data.time))
                self.downloaded += getattr(udp_data, 'len') - 8
            else:
                self.transmission_timestamps.append(float(raw_data.time))
                self.uploaded += getattr(udp_data, 'len') - 8
                
        flags = raw_data['UDP'].flags # Correct way to get flags
        self.flags.append(flags)
    
    def serialize(self) -> dict:
        if self.app_layer:
            return self.app_layer.serialize('UDP', self.ip_packet)
        r_avg, t_avg = self.get_average_timestamps()
        return {
            'ip': self.ip_packet.serialize(),
            's_port': self.s_port,
            'd_port': self.d_port,
            'download': self.downloaded,
            'upload': self.uploaded,
            'protocol': self.protocol,
            'start_time': get_date(self.transmission_timestamps[0]) if len(self.transmission_timestamps) > 0 else '',
            'avg_rec_time': r_avg,
            'avg_trans_time': t_avg,
        }

    def get_download(self) -> int:
        return self.downloaded

    def get_upload(self) -> int:
        return self.uploaded

    def get_average_timestamps(self) -> tuple:
        r_avg, t_avg = (0.0, 0.0)
        for r_time, t_time in zip_longest(self.reception_timestamps, self.transmission_timestamps):
            r_avg += r_time if r_time else 0
            t_avg += t_time if t_time else 0
        r_avg = r_avg / len(self.reception_timestamps) if len(self.reception_timestamps) != 0 else -1
        t_avg = t_avg / len(self.transmission_timestamps) if len(self.transmission_timestamps) != 0 else -1
        r_avg = datetime.datetime.utcfromtimestamp(r_avg).microsecond/1000
        t_avg = datetime.datetime.utcfromtimestamp(t_avg).microsecond/1000
        return (r_avg, t_avg)

    def is_dns(self) -> bool:
        return True if self.app_layer else False

    def dns_or_download(self) -> str:
        '''
        If it has UDP data then UDP related info will be printed
        Else upload/download will be printed
        '''
        if self.app_layer:
            return f'{self.app_layer}'
        else:
            return f'Download: {self.downloaded}, Upload: {self.uploaded}'

    def __str__(self):
        r_avg, t_avg = self.get_average_timestamps()
        return f'{self.ip_packet} {self.s_port}->{self.d_port}, UDP:{self.protocol} {self.dns_or_download()}, Avg Rec/Tra Gap: {r_avg}/{t_avg}'
    
    def get_flags(self):
        return self.flags
class DNS:
    '''
    To store DNS related info
    '''
    record_type = None
    query_response_time = None
    query_initiated = 0 
    domain_name = '' # It is not necessary for this to be a domain name, consider it as query
    ip_address = None # It is not necessary for this to be IP, consider it to be a response

    def __init__(self, raw_data):
        dns_data = raw_data['DNS']
        dns_qd = getattr(dns_data, 'qd')
        self.record_type = dns_types[getattr(dns_qd, 'qtype')] if dns_types[getattr(dns_qd, 'qtype')] else 'UNKNOWN'
        if getattr(dns_data, 'ra') == 0:
            # The initial DNS can or cannot be a query
            # If it is a query we do set query_initiated
            self.query_initiated = float(raw_data.time)
        self.domain_name = getattr(dns_qd, 'qname').decode('utf-8')

    def update(self, raw_data, swap=False):
        dns_data = raw_data['DNS']
        if swap:
            dns_an = getattr(dns_data, 'an')
            if dns_an:
                if self.record_type in ['A', 'AAAA', 'MX', 'NS', 'SRV', 'PTR']:
                    response = getattr(dns_an, 'rdata')
                    if type(response) == bytes:
                        response = response.decode('utf-8')
                    self.ip_address = response 
                    # E.g. google.com. => ['google', 'com', '']
                    if response.split('.')[-1] == '' and self.record_type in ['A', 'AAAA']:
                        self.record_type = 'CNAME'
                if self.query_initiated:
                    dt = float(raw_data.time)
                    self.query_response_time = dt - self.query_initiated
                    dt = datetime.datetime.utcfromtimestamp(self.query_response_time)
                    self.query_response_time = dt.microsecond/1000

    def serialize(self, transport_layer: str, ip_layer: IPPacket) -> dict:
        return {
            'type': 'DNS',
            'ip': ip_layer.serialize(),
            'requested_domain': self.domain_name,
            'response_ip': self.ip_address,
            'record_type': self.record_type,
            'response_time': self.query_response_time,
            'start_time': get_date(self.query_initiated)
        }

    def __str__(self):
        return f'{self.domain_name}->{self.ip_address}, {self.record_type} in {self.query_response_time}ms'