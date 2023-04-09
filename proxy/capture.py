from scapy.all import *
import requests
from packetenizer.core import CoreStructure
from packetenizer.repeated_timer import RepeatedTimer
from packetenizer.helper.analyzer import analyze

core_structure = CoreStructure()

cap = sniff(iface="en0", prn=lambda x : core_structure.start(x), store=0)

network_map = {
    "id": "123.123.13.13"
}

block_map = {
    "id": ["yo"]
}

def load_block_map(id):
    pass

def test():
    print("test")
    analyzed, problem_ips = analyze(core_structure)
    serialized = core_structure.serialize(analyzed, problem_ips)
    tcp = serialized['tcp']

    for connection in tcp:
        dest_addr = connection['ip']['destination_address']
        src_addr = connection['ip']['source_address']
        print(dest_addr, src_addr)
        payload = "".join(str(connection["payload"]))
        print(payload)

        ## Make request for tracking that uses dest_addr
        response = requests.post("http://localhost:5000/filter/checkurl", {
            "url": "https://google.com",
            "parent": "64312bf5273fe0519c501835",
            "child": "6431a352b841ac888899d75d"
        })
        print(response.content)
        ## Check for content allowance
        response = requests.post("http://localhost:5000/filter/content", {
            "content": "".join(payload)
        })
        print(response.content)

RepeatedTimer(5, test)