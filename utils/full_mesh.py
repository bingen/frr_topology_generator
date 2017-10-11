#!/usr/bin/python3

import sys

def get_ip_body(i, j):
    if i < j:
        return str(i) + "." + str(j)
    else:
        return str(j) + "." + str(i)
def generate_zebra_config_file(i, nodes, folder):
    with open(folder+"/zebra-" + str(i) + ".conf", "w") as f:
        f.write("interface lo\n")
        f.write(" ip address 1.0.0." + str(i) + "/32\n")
        for j in range(1, nodes+1):
            if i == j:
                continue
            f.write("interface " + str(i) + "-xge"+ str(j) + "\n")
            f.write(" ip address 1." + get_ip_body(i, j) + "." + str(i) + "/24\n")
def generate_ospf_config_file(i, nodes, folder):
    with open(folder+"/ospfd-" + str(i) + ".conf", "w") as f:
        f.write("router ospf\n")
        f.write(" ospf router-id 1.0.0." + str(i) + "\n")
        f.write(" network 1.0.0." + str(i) + "/32 area 0.0.0.0\n")
        for j in range(1, nodes+1):
            if i == j:
                continue
            f.write(" network 1." + get_ip_body(i, j) + ".0/24 area 0.0.0.0\n")
def generate_bgp_config_file(i, nodes, folder):
    BGP_ID = "65000"
    with open(folder+"/bgpd-" + str(i) + ".conf", "w") as f:
        f.write("router bgp " + BGP_ID + "\n")
        f.write(" bgp router-id 1.0.0." + str(i) + "\n")
        for j in range(1, nodes+1):
            if i == j:
                continue
            f.write(" neighbor 1." + get_ip_body(i, j) + "." + str(j) + \
                    " remote-as " + BGP_ID + "\n")

def generate_config_files(nodes, folder):
    for i in range(1, nodes+1):
        generate_zebra_config_file(i, nodes, folder)
        generate_ospf_config_file(i, nodes, folder)
        generate_bgp_config_file(i, nodes, folder)

def generate_dot_file(nodes):
    with open("full_mesh_" + str(nodes) + ".dot", 'w') as f:
        f.write("graph test {\n")
        for i in range(1, nodes+1):
            for j in range (i+1, nodes+1):
                f.write(str(i) + " -- " + str(j) + "\n")
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
