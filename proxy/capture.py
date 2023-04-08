from scapy.all import *
from packetenizer.core import CoreStructure

core_structure = CoreStructure()

cap = sniff(iface="eth0", prn=lambda x : core_structure.start(x), store=0)