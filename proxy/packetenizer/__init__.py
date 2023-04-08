from scapy.error import Scapy_Exception
from scapy.all import rdpcap
from packetenizer.core import CoreStructure
from packetenizer.helper.analyzer import analyze
import traceback
from io import BufferedReader

def parse_and_analyze(uploaded_file):
    try:
        print(uploaded_file)
        parsed_file = rdpcap(uploaded_file)
        core_structure = CoreStructure(parsed_file)
        core_structure.start()
        aggregated_dict = {}
        problem_ips = []
        aggregated_dict, problem_ips = analyze(core_structure, uploaded_file)
        serialized_dict = core_structure.serialize(aggregated_dict, problem_ips)
    except Scapy_Exception:
        return "Scapy failed to parse file", False
    except Exception as e:
        traceback.print_exc()
        print(e)
        return "Unknown Error", False
    return serialized_dict, True