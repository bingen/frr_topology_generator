#!/usr/bin/python3

import sys

BRIDGE_SUBNET_PREFIX='172.17.0.'
LOOPBACK_PREFIX='10.0.0.'
NEIGHBOR_PREFIX='10.0.1.'

BGP_ID = "65000"

def get_ip_body(i, j):
    if i < j:
	return str(i) + "." + str(j)
    else:
	return str(j) + "." + str(i)
def generate_zebra_config_file(i, nodes, folder):
    with open(folder+"/zebra-" + str(i) + ".conf", "w") as f:
	f.write("interface lo\n")
	f.write(" ip address " + LOOPBACK_PREFIX + str(i) + "/32\n")
	f.write("interface eth0\n")
	f.write(" ip address " + BRIDGE_SUBNET_PREFIX + str(i+1) + "/16\n")
def generate_ospf_config_file(i, nodes, folder):
    with open(folder+"/ospfd-" + str(i) + ".conf", "w") as f:
	f.write("router ospf\n")
	f.write(" ospf router-id " + LOOPBACK_PREFIX + str(i) + "\n")
	f.write(" network " + LOOPBACK_PREFIX + str(i) + "/32 area 0.0.0.0\n")
	f.write(" network " + BRIDGE_SUBNET_PREFIX + "0/16 area 0.0.0.0\n")
def generate_isis_config_file(i, nodes, folder):
    with open(folder+"/isisd-" + str(i) + ".conf", "w") as f:
	f.write("interface lo\n")
	f.write(" ip router isis TEST\n")
	f.write("interface eth0\n")
	f.write(" ip router isis TEST\n")
	if (i == 1):
	    f.write("interface eth1\n")
	    f.write(" ip router isis TEST\n")
	f.write("router isis TEST\n")
	f.write(" net 49.0001.0000.0000." + str(i+6).zfill(4) + ".00\n")
	f.write(" metric-style wide\n")
def generate_bgp_config_file(i, nodes, folder):
    if (i == 1):
	return
    BGP_ID = "666"
    with open(folder+"/bgpd-" + str(i) + ".conf", "w") as f:
	f.write("router bgp " + BGP_ID + "\n")
	if i == 1:
	    for j in range(2, nodes+1):
		f.write(" neighbor " + BRIDGE_SUBNET_PREFIX + str(j+1) + \
			" remote-as " + BGP_ID + "\n")
	else:
	    f.write(" neighbor " + NEIGHBOR_PREFIX + "2" + \
		    " remote-as " + BGP_ID + "\n")

def generate_config_files(nodes, folder):
    for i in range(1, nodes+1):
	generate_zebra_config_file(i, nodes, folder)
	generate_ospf_config_file(i, nodes, folder)
	generate_isis_config_file(i, nodes, folder)
	generate_bgp_config_file(i, nodes, folder)

def generate_dot_file(nodes):
    with open("star_" + str(nodes) + ".dot", 'w') as f:
	f.write("graph test {\n")
	for j in range (2, nodes+1):
	    f.write("1 -- " + str(j) + "\n")
	f.write("}\n")

def main(args):
    nodes = int(args[0])
    if nodes <= 0:
	print("Nodes must be a positive integer")
	exit(1)
    folder = args[1]

    generate_dot_file(nodes)
    generate_config_files(nodes, folder)

if __name__ == '__main__':
    main(sys.argv[1:])
