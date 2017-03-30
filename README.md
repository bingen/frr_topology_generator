FRR topology generator
========================

This repository starts containers, links bridges, creates byobu sessions and starts daemons given a network topology in .DOT format.

Instructions
------------

- Run:

    ./tg.py -f topology.dot

where file.dot is the source file containing the topology in DOT format used by GraphViz.

A minimal example of a DOT file:

    graph topology {
    1 -- 2
    1 -- 3
    2 -- 4
    3 -- 4
    }

An image of the topology can be generated with graphviz package:

    dot -Tpng topology.dot -o topology.png
