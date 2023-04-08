from scapy.all import *
from packetenizer.core import CoreStructure
from packetenizer.repeated_timer import RepeatedTimer
from packetenizer.helper.analyzer import analyze

core_structure = CoreStructure()

cap = sniff(iface="eth0", prn=lambda x : core_structure.start(x), store=0)

def test():
    print("test")
    analyzed, problem_ips = analyze(core_structure)
    print(core_structure.serialize(analyzed, problem_ips))

RepeatedTimer(5, test)