#!/usr/bin/python3

import sys
import getopt
import subprocess
import os
import docker
import json

BRIDGE_SUBNET_PREFIX='10.'
DOCKER_IMAGE = "frr/docker-frr"
CONTAINER_BASE_NAME="frr"
CONTAINER_BASE_PATH='/root/'
CONTAINER_WORKSPACE_PATH=CONTAINER_BASE_PATH + 'workspace'
BYOBU_SCRIPT_CONTAINER = "byobu_container.sh"
RENAME_IFACE_SCRIPT = "rename_iface.sh"
DOCKER_SERVER_VERSION="1.24"
# default values for command line options
SHELL='zsh'
BASE_PATH_MAIN = os.path.expanduser("~") + "/workspace"
ZEBRA_CONF_FILES_FOLDER = "test"

def process_args(args):
    global SHELL, BASE_PATH_MAIN, ZEBRA_CONF_FILES_FOLDER
    file_path = ""
    try:
        opts, _ = getopt.getopt(args, "hf:s:w:n:z:", longopts=[])
    except getopt.GetoptError:
        print("Error getting opts")
        return file_path

    for opt, arg in opts:
        if opt in '-h':
            print("Usage: ./tg.py [OPTIONS]")
            print("-h				Display this help")
            print("-f file				Source file")
            print("-s shell			Shell")
            print("-w path				Workspace base path")
            print("-z path				Zebra conf files folder (relative from workspace in container)")
            exit(0)
        elif opt in "-f":
            file_path = arg
        elif opt in "-s":
            SHELL = arg
        elif opt in "-w":
            BASE_PATH_MAIN = arg
        elif opt in "-z":
            ZEBRA_CONF_FILES_FOLDER = arg

    if file_path == "":
        print("You must specify a source file!")
        exit (1)

    print("Source file: " + file_path)
    print("Shell: " + SHELL)
    print("Workspace base path: " + BASE_PATH_MAIN)
    print("Zebra configuration files folder: " + ZEBRA_CONF_FILES_FOLDER)
    print("")
    return file_path

def process_file(file_path):
    nodes = [] # Network nodes
    links = []

    f = open(file_path)
    for line in f:
        # skip lines that don't represent links between nodes
        if not '--' in line:
            continue

        # remove ending newline
        line = line.replace('\n', '')
        # print(line)

        # remove options in brackets
        v = line.split('[')
        line_aux = v[0]

        # find nodes
        v = line_aux.split('--')
        if len(v) != 2:
            print("Malformed line!")
            print(line_aux)
            print(v)
            continue

        # add link
        links.append([v[0].strip(), v[1].strip()])

        # loop through nodes
        for i in v:
            node = i.strip()
            if not node in nodes:
                nodes.append(node)

    f.close()

    #print(nodes)
    #print(links)
    return nodes, links

def create_bridges(nodes, links):
    spare_bridges = {}
    client = docker.from_env(version=DOCKER_SERVER_VERSION)
    b = 0 # bridge index, to allow more than 1 link among 2 nodes
    for link in links:
        b = b + 1
        bridge_name = "docker-" + str(b) + "-" + link[0] + "-" + link[1]
        ipam_pool = docker.types.IPAMPool(
            subnet=BRIDGE_SUBNET_PREFIX + link[0] + "." + link[1] + '.0/24',
            gateway=BRIDGE_SUBNET_PREFIX + link[0] + "." + link[1] + '.1'
        )
        ipam_config = docker.types.IPAMConfig(
            pool_configs=[ipam_pool]
        )
        network = client.networks.create(bridge_name, driver="bridge",
                                         ipam=ipam_config)#, enable_ipv6=True)
        # store docker network(bridge) in link vector
        link.append(network)
    # generate unpaired bridges to allow connections to outside
    for node in nodes:
        b = b + 1
        bridge_name = "docker-" + str(b) + "-" + node + "-" + node
        ipam_pool = docker.types.IPAMPool(
            subnet=BRIDGE_SUBNET_PREFIX + node + '.' + node + '.0/24',
            gateway=BRIDGE_SUBNET_PREFIX + node + '.' + node + '.1'
        )
        ipam_config = docker.types.IPAMConfig(
            pool_configs=[ipam_pool]
        )
        network = client.networks.create(bridge_name, driver="bridge",
                                         ipam=ipam_config)#, enable_ipv6=True)
        # store docker network(bridge) in link vector
        spare_bridges[node] = network
    return spare_bridges
def generate_docker_image():
    client = docker.from_env(version=DOCKER_SERVER_VERSION)
    client.images.build(path='docker', tag=DOCKER_IMAGE)
    #print (client.images.list())

def add_container_to_ssh_config(host, ip):
    ssh_config = os.path.expanduser('~/.ssh/config')
    with open(ssh_config) as file:
        if host in file.read():
            return

    entry = """
Host """ + host + """
    Hostname """ + ip + """
    User root
    IdentityFile ~/.ssh/container_rsa
    StrictHostKeyChecking no
"""
    with open(ssh_config, 'a') as file:
        file.write(entry)

def generate_containers(nodes):
    va_nevi_addr = {}
    client = docker.from_env(version=DOCKER_SERVER_VERSION)
    for node in nodes:
        container_name = CONTAINER_BASE_NAME + node
        client.containers.run(DOCKER_IMAGE,
                              volumes={BASE_PATH_MAIN:
                                       {'bind': CONTAINER_WORKSPACE_PATH, 'mount': 'rw'}},
                              privileged=True,
                              detach=True, #tty=True,
                              name=container_name)
        kemestas = client.containers.get(container_name)
        # Get IP address
        ip_address = kemestas.attrs['NetworkSettings']['Networks']['bridge']['IPAddress']
        print("IP Address: " + ip_address)

        # Add container to ssh config
        add_container_to_ssh_config(container_name, ip_address)

    # add container key to ~/.ssh
    subprocess.call("/bin/bash -c '[[ -f ~/.ssh/container_rsa.pub ]] || cp docker/utils/container_rsa.pub ~/.ssh/'",
                    shell=True)
    subprocess.call("/bin/bash -c '[[ -f ~/.ssh/container_rsa ]] || cp docker/utils/container_rsa ~/.ssh/'",
                    shell=True)
    subprocess.call("chmod 0400 ~/.ssh/container_rsa", shell=True)

def rename_iface(node, prefix, iface):
    client = docker.from_env(version=DOCKER_SERVER_VERSION)
    kemestas = client.containers.get(node)
    rename_iface_command = CONTAINER_BASE_PATH + RENAME_IFACE_SCRIPT + " " + prefix + " " + iface
    #print(node + ": " + rename_iface_command)
    kemestas.exec_run(rename_iface_command)
def connect_containers(links):
    for link in links:
        node1 = CONTAINER_BASE_NAME + link[0]
        node2 = CONTAINER_BASE_NAME + link[1]
        # connect container to docker network/bridge, stored in link[2]
        network = link[2]
        network.connect(node1)
        network.connect(node2)
        # Change iface name
        # TODO: check that it's not already used. It will only happen in case
        # 2 different links are used to connect the same machines
        print(link[0] + "-xge" + link[1], link[1] + "-xge" + link[0])
        subnet = network.attrs['IPAM']['Config'][0]['Subnet']
        prefix = subnet[0:subnet.find('.0')]
        print(prefix)
        # first node
        rename_iface(node1, prefix, link[0] + "-xge" + link[1])
        # second node
        rename_iface(node2, prefix, link[1] + "-xge" + link[0])
def connect_spare_bridges(nodes, spare_bridges):
    for node in nodes:
        node_name = CONTAINER_BASE_NAME + node
        network = spare_bridges[node]
        network.connect(node_name)
        # Change iface name
        iface_name = node + "-xge" + node
        print(iface_name)
        subnet = network.attrs['IPAM']['Config'][0]['Subnet']
        prefix = subnet[0:subnet.find('.0')]
        print(prefix)
        rename_iface(node_name, prefix, iface_name)

def start_containers(nodes):
    client = docker.from_env(version=DOCKER_SERVER_VERSION)
    for node in nodes:
        container_name = CONTAINER_BASE_NAME + node
        kemestas = client.containers.get(container_name)
        # Generate byobu
        ip_address = kemestas.attrs['NetworkSettings']['Networks']['bridge']['IPAddress']
        byobu_container_command = \
            CONTAINER_BASE_PATH + BYOBU_SCRIPT_CONTAINER + " " + \
            SHELL + " " + CONTAINER_WORKSPACE_PATH + " " + node + " " + \
            ip_address + " " + ZEBRA_CONF_FILES_FOLDER
        print(byobu_container_command)
        kemestas.exec_run(byobu_container_command)#, detach=True, tty=True)

def generate_topology(nodes, links):
    # Bridges
    spare_bridges = create_bridges(nodes, links)

    # generate and run containers
    generate_docker_image()
    generate_containers(nodes)
    connect_containers(links)
    connect_spare_bridges(nodes, spare_bridges)

    # run container byobus
    start_containers(nodes)

def main(args):
    file_path = process_args(args)
    nodes, links = process_file(file_path)
    generate_topology(nodes, links)

    # generate png file:
    subprocess.call(['dot', '-Tpng', file_path, '-o', file_path + '.png'])

if __name__ == '__main__':
    main(sys.argv[1:])
