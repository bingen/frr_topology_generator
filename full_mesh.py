import sys

def main(args):
    nodes = int(args[0])
    if nodes <= 0:
        print("Nodes must be a positive integer")
        exit(1)

    with open("full_mesh_" + str(nodes) + ".dot", 'w') as f:
        f.write("graph test {\n")
        for i in range(1, nodes+1):
            for j in range (i+1, nodes+1):
                f.write(str(i) + " -- " + str(j) + "\n")
        f.write("}\n")

if __name__ == '__main__':
    main(sys.argv[1:])
