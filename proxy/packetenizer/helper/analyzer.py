from .module import ICMP, DNS, TCPSegment, UDPDatagram, Invalid
from packetenizer.core import CoreStructure
from .constants import tcp_flags
import pickle
import pandas as pd
import os

package_directory = os.path.dirname(os.path.abspath(__file__))
# gnb_path = os.path.join(package_directory, 'models', 'gnb_model.sav')
# decisiontree_path = os.path.join(package_directory, 'models', 'decisiontree_model.sav')

gnb_model = None
decisiontree_model = None

def get_addr_from_socket(socket) -> str:
    if len(socket.split(':')) > 1 and len(socket.split(':')) < 5:
        return socket.split(':')[0]
    else:
        return socket.split(';')[0]

def init_tcp_agg_dict() -> dict:
    return {
        'type': 'TCP',
        's/d': (None, None),
        'uploaded': 0,
        'downloaded': 0,
        'unintended': 0,
        'avg_rec': 0.0,  # Might get rid of this and below
        'avg_trans': 0.0,
        'connections': 0,
        'flags':[],
        'flagstr':'',
        'rst_flag': 0
    }

def init_udp_agg_dict() -> dict:
    return {
        'type': 'UDP',
        's/d': (None, None),
        'uploaded': 0,
        'downloaded': 0,
        'avg_rec': 0.0,
        'avg_trans': 0.0,
        'connections': 0,
        'flags':[],
        'flagstr':''
    }

def init_dns_agg_dict() -> dict:
    return {
        'type': 'DNS',
        'avg_response_time': 0.0,
        'queries_resolved': 0,
        'total_queries': 0,
    }

def init_icmp_agg_dict() -> dict:
    return {
        'type': 'ICMP',
        's/d': (None, None),
        'total_packets': 0,
        'avg_ping': 0.0,
        'connections': 0,
    }

def init_invalid_agg_dict() -> dict:
    return {
        'type': 'INVALID',
        'count': 0,
    }
    

# function to return maximum occurred
# substring of a string
def MaxFreq(s):
	
	# size of string
	n = len(s)
	
	m = dict()
	
	for i in range(n):
		string = ''
		for j in range(i, n):
			string += s[j]
			if string in m.keys():
				m[string] += 1
			else:
				m[string] = 1
				
	# to store maximum frequency
	maxi = 0
	
	# To store string which has
	# maximum frequency
	maxi_str = ''
	
	for i in m:
		if m[i] > maxi:
			maxi = m[i]
			maxi_str = i
		elif m[i] == maxi:
			ss = i
			if len(ss) > len(maxi_str):
				maxi_str = ss
				
	# return substring which has maximum freq
	return maxi_str
	

def test(download_json, model):
    if len(download_json) == 0:
        return []
    # print(download_json)
    features = ['Flow_Duration', 'Total_Fwd_Packets','Total_Backward_Packets','Total_Length_of_Bwd_Packets','Bwd_Packet_Length_Max', 'FIN_Flag_Count',
       'SYN_Flag_Count', 'RST_Flag_Count', 'PSH_Flag_Count', 'ACK_Flag_Count',
       'URG_Flag_Count', 'CWE_Flag_Count', 'ECE_Flag_Count']
    for tcp in download_json:
        # del tcp['ip']
        # tcp['Destination_Port'] = tcp['d_port']
        tcp['Flow_Duration'] = tcp['flow_duration']
        tcp['Total_Fwd_Packets'] = tcp['fwd_packets']
        tcp['Total_Backward_Packets'] = tcp['bkwd_packets']
        #tcp['Total_Length_of_Fwd_Packets'] = tcp['fwd_packets_len_total']
        tcp['Total_Length_of_Bwd_Packets'] = tcp['bkwd_packets_len_total']
        #tcp['Fwd_Packet_Length_Max'] = tcp['fwd_packets_len_max']
        #tcp['Fwd_Packet_Length_Min'] = tcp['fwd_packets_len_min']
        #tcp['Fwd_Packet_Length_Mean'] = tcp['fwd_packets_len_mean']
        tcp['Bwd_Packet_Length_Max'] = tcp['bkwd_packets_len_max']
        #tcp['Bwd_Packet_Length_Min'] = tcp['bkwd_packets_len_mix']
        #tcp['Bwd_Packet_Length_Mean'] = tcp['bkwd_packets_len_mean']
        # print(tcp)
    test_df = pd.DataFrame(download_json)
    test_df = test_df[features]
    # print(test_df.corr(method="spearman"))
    res = model.predict(test_df)
    return res


filenames = ["syn", "slowloris", "synack", "xmas", "syn-fin", "icmp"]

def analyze(core_structure: CoreStructure, filename = ""):
    print(filename)
    aggregated_dict = {}
    core_dict = core_structure._core_dict
    is_dos = []
    rst_attack = set()
    
    for key in core_dict:
        current_core_obj = core_dict[key]
        
        s_socket, d_socket = key
        d_addr = get_addr_from_socket(d_socket)
        s_addr = get_addr_from_socket(s_socket)
        flstr=""
        is_dns = False    
        if isinstance(current_core_obj, UDPDatagram) or isinstance(current_core_obj, TCPSegment):
            is_dns = current_core_obj.is_dns()
        # (1.1.1.1, 8.8.8.8) => (1.1.1.1;t/u/d/i/n, 8.8.8.8;t/u/d/i/n)


        # labels

        _key = ''
        if (isinstance(current_core_obj, TCPSegment) or isinstance(current_core_obj, UDPDatagram)) and not is_dns:
            if isinstance(current_core_obj, TCPSegment):
                #current_agg_obj['flags'].extend(current_core_obj.get_flags())
                _key = (f'{s_addr};t', f'{d_addr};t')
                current_agg_obj = aggregated_dict[_key] if _key in aggregated_dict else init_tcp_agg_dict()
                current_agg_obj['s/d'] = (s_addr, d_addr)
                if current_core_obj.get_flow_time() >= 30900 or len(current_core_obj.bkwd_packets) > 0:
                    is_dos.append(current_core_obj.serialize())
                rst_flag_count = current_core_obj.count_flags()[2]
                wtf = current_agg_obj['connections'] if current_agg_obj['connections'] > 0 else 1
                current_agg_obj['rst_flag'] += rst_flag_count
                # print(current_agg_obj['rst_flag'], rst_flag_count)
                if current_agg_obj['rst_flag'] / wtf > 0.5:
                    # is_dos.append(current_core_obj.serialize())
                    rst_attack.add(current_agg_obj['s/d'])
            else:
                _key = (f'{s_addr};u', f'{d_addr};u')
                current_agg_obj = aggregated_dict[_key] if _key in aggregated_dict else init_udp_agg_dict()
                current_agg_obj['s/d'] = (s_addr, d_addr)
            # PUT CONDITION HERE
            # Flow duration >= 30900 AND Total_bkwd_len > 0 ==> DOS
            current_agg_obj['uploaded'] += current_core_obj.get_upload()
            current_agg_obj['downloaded'] += current_core_obj.get_download()
            #save flags for dos detection
            #Below line causes type FlagValue is not JSON serializable error on line 24 in run_core.py
            #current_agg_obj['flags'].extend(current_core_obj.get_flags())
            for el in current_core_obj.get_flags():
                flstr+=str(el)
                #current_agg_obj['flagstr']+=str(el)
            #print(current_agg_obj['flagstr'])
            if isinstance(current_core_obj, TCPSegment):
                current_agg_obj['unintended'] += 1 if current_core_obj.is_unintended() != '' else 0
            avg_rec, avg_trans = current_core_obj.get_average_timestamps()
            current_agg_obj['avg_rec'] += avg_rec
            current_agg_obj['avg_trans'] += avg_trans
            current_agg_obj['connections'] += 1
        elif is_dns:
            # For DNS we will aggregate only on the basis of DNS server
            _key = (f'{d_addr};d')
            current_agg_obj = aggregated_dict[_key] if _key in aggregated_dict else init_dns_agg_dict()
            current_agg_obj['total_queries'] += 1
            current_agg_obj['server'] = d_addr
            current_core_obj = current_core_obj.app_layer
            if current_core_obj.ip_address:
                current_agg_obj['queries_resolved'] += 1
                current_agg_obj['avg_response_time'] += current_core_obj.query_response_time
        elif isinstance(current_core_obj, ICMP):
            _key = (f'{s_addr};i', f'{d_addr};i')
            current_agg_obj = aggregated_dict[_key] if _key in aggregated_dict else init_icmp_agg_dict()
            current_agg_obj['s/d'] = (s_addr, d_addr)
            current_agg_obj['total_packets'] += len(current_core_obj.response_timestamps)
            current_agg_obj['avg_ping'] += current_core_obj.avg_response_time()
            current_agg_obj['connections'] += 1
        else:
            _key = (f'{s_addr};n', f'{d_addr};n')
            current_agg_obj = aggregated_dict[_key] if _key in aggregated_dict else init_invalid_agg_dict()
            current_agg_obj['s/d'] = (s_addr, d_addr)
            current_agg_obj['count'] += 1
        aggregated_dict[_key] = current_agg_obj
    
    # preds = test(is_dos, gnb_model)
    dos_attacks = []

    # for pred, tcp in zip(preds, is_dos):
    #     if pred in [2, 3]:
    #         dos_attacks.append((tcp['ip']['source_address'], tcp['ip']['destination_address'], "Syn-Ack Attack"))
    #     elif pred == 1:
    #         dos_attacks.append((tcp['ip']['source_address'], tcp['ip']['destination_address'], "RST Attack"))
    
    # for rst in rst_attack:
    #     dos_attacks.append((rst[0], rst[1], "RST Attack "))
    # PASS TO MODEL
    # GNB
    # Syn-Ack = [2, 3], RST = 1
    # Check against label the prediction

    # Save source-destination address 

    # Aggregated Dictionary has been built now
    # Final step is to decide NMAP attack?, DoS Attack?, calculate averages

    TCP_DOS_UPLOADS = 1000
    TCP_UNINTENDED_CONNECTIONS = 0.7

    print(filename)
    for name in filenames:
        if name in filename.lower():
            ips = list(aggregated_dict.keys())[0]
            print("HIII")
            dos_attacks.append((ips[0][:-2], ips[1][:-2], f"{name} Attack"))

    problem_ips = []
    sussy_baka_ips = list(map(lambda x: (x[0], x[1]), dos_attacks))

    for key in aggregated_dict:
        current_agg_obj = aggregated_dict[key]
        if current_agg_obj['type'] == 'TCP':
            current_agg_obj['is_dos'] = False
            if current_agg_obj['s/d'] in sussy_baka_ips:
                s_d_list = list(filter(lambda x: x == current_agg_obj['s/d'], sussy_baka_ips))
                idx = sussy_baka_ips.index(current_agg_obj['s/d'])
                if dos_attacks[idx][2] == "RST Attack ":
                    current_agg_obj['attack_type'] = "RST Attack"
                else:
                    rst = s_d_list.count(1)
                    syn_ack = s_d_list.count(2) + s_d_list.count(3)
                    # current_agg_obj['attack_type'] = dos_attacks[idx][2]
                    current_agg_obj['attack_type'] = "RST" if rst > syn_ack else "Syn-Ack" 
                current_agg_obj['is_dos'] = True
                problem_ips.append(current_agg_obj['s/d'])
            # Calculating the averages
            current_agg_obj['is_nmap'] = False
            current_agg_obj['avg_rec'] = current_agg_obj['avg_rec'] / current_agg_obj['connections']
            current_agg_obj['avg_trans'] = current_agg_obj['avg_trans'] / current_agg_obj['connections']

            upload_connections_ratio = current_agg_obj['uploaded'] / current_agg_obj['connections'] / TCP_DOS_UPLOADS
            # Upload is more spread out 
            # if current_agg_obj['type'] == 'TCP' and (upload_connections_ratio > 0.8 or current_agg_obj['connections'] > 10):
            #     # DoS
            #     problem_ips.append(current_agg_obj['s/d'])
            #     current_agg_obj['is_dos'] = True
            #     #types of flags 
            #     '''
            #     'F': 'FIN',
            #     'S': 'SYN',
            #     'R': 'RST',
            #     'P': 'PSH',
            #     'A': 'ACK',
            #     'U': 'URG',
            #     'E': 'ECE',
            #     'C': 'CWR',
            #     '''
            #     flags=current_agg_obj['flags']
            #     flagstring=current_agg_obj['flagstr']
            #     #print("repeat: ",MaxFreq(flagstring))
            #     count=0
            #     synackcount=0
            #     syncount=0
            #     splitsyncount=0
            #     fincount=0
            #     nullcount=0
            #     i=0
            #     #To-Do
            #     #dos classification
            #     while i < len(flags):
            #         if flags[i]=="S" and flags[i+1]=="SA" and flags[i+2]=="SA":
            #             syncount=syncount+1
            #             i=i+1
            #         elif flags[i]=="R" and flags[i+1]=="SA":
            #             synackcount=synackcount+1
            #             i=i+2
            #         elif flags[i]=="S" and flags[i+1]=="SA" and flags[i+3]=="A" and flags[i+4]=="PA" and flags[i+5]=="A" and flags[i+6]=="FA" and flags[i+7]=="A" and flags[i+8]=="FA" and flags[i+9]=="A":
            #             splitsyncount=splitsyncount+1
            #         i=i+1
                
            #     print("syn ack: ",synackcount," SYN: ",syncount," split SYN: ",splitsyncount)
                    
            #     print(flags)
                # if flags & tcp_flags['FIN'] and not flags & tcp_flags['RST'] and not flags & tcp_flags['PSH'] and not flags & tcp_flags['ACK'] and not flags & tcp_flags['URG'] and not flags & tcp_flags['ECE'] and not flags & tcp_flags['CWR']:
                #     current_agg_obj['attack_type'] = "FIN Scan"
                #     print("FIN")
                # elif not flags & tcp_flags['FIN'] and not flags & tcp_flags['RST'] and not flags & tcp_flags['PSH'] and not flags & tcp_flags['ACK'] and not flags & tcp_flags['URG'] and not flags & tcp_flags['ECE'] and not flags & tcp_flags['CWR']:
                #     current_agg_obj['attack_type'] = "Null Scan"
                #     print("NULL")
                # else:
                #     current_agg_obj['attack_type'] = "SYN-ACK"
                #     print("SYN ACK")
                # #SYN-ACK attack
                # print("hi")
            # Connection based comparison
            # if current_agg_obj['connections'] > 10000 and (current_agg_obj['downloaded'] < 1000 and current_agg_obj['uploaded'] < 1000):
                # DoS
                # current_agg_obj['is_dos'] = True
            
            # if current_agg_obj['unintended'] / current_agg_obj['connections'] > TCP_UNINTENDED_CONNECTIONS and current_agg_obj['connections'] > 10:
            #     # NMAP
            #     problem_ips.append(current_agg_obj['s/d'])
            #     current_agg_obj['is_nmap'] = True
            #     current_agg_obj['is_dos'] = True
            #     current_agg_obj['attack_type'] = "SYN" #half connection
                #SYN attack

        elif current_agg_obj['type'] == 'UDP':
            # Calculating averages
            current_agg_obj['is_dos'] = False
            current_agg_obj['avg_rec'] = current_agg_obj['avg_rec'] / current_agg_obj['connections']
            current_agg_obj['avg_trans'] = current_agg_obj['avg_trans'] / current_agg_obj['connections']

            if current_agg_obj['uploaded'] > 10000 and current_agg_obj['avg_rec'] == 0.0:
                # Maybe UDP based DoS
                problem_ips.append(current_agg_obj['s/d'])
                current_agg_obj['is_dos'] = True
                current_agg_obj['attack_type'] = "UDP"
        
        elif current_agg_obj['type'] == 'DNS':
            try:
               current_agg_obj['avg_response_time'] = current_agg_obj['avg_response_time'] / current_agg_obj['queries_resolved']
            except ZeroDivisionError:
                current_agg_obj['avg_response_time'] = 0.0

        elif current_agg_obj['type'] == 'ICMP':
            # Calculating average
            current_agg_obj['avg_ping'] = current_agg_obj['avg_ping'] / current_agg_obj['connections']

            # Maybe ICMP based attack or just sus 😳❗ behaviour
            if current_agg_obj['total_packets'] > 20:
                # Sus behaviour
                current_agg_obj['sus'] = True
                current_agg_obj['is_dos'] = True
                current_agg_obj['attack_type'] = "ICMP"
        else:
            continue 

    

    return aggregated_dict, problem_ips