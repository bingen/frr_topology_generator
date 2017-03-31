FRR topology generator
========================

This repository starts containers, links bridges, creates byobu sessions and starts [FRR](https://github.com/FRRouting/frr) daemons given a network topology in .DOT format.

Dependencies
------------

- Those of [FRR](https://github.com/FRRouting/frr/blob/master/doc/Building_FRR_on_Debian8.md)
- [Docker](https://store.docker.com/editions/community/docker-ce-server-debian?tab=description)

Description
-----------

This script is intended to help with FRR manual testing, not for completely automated testing like CI (FRR already has that). You must previously have FRR compiled and config files created in a common parent folder. Something like this:

    ~
    |
    └── workspace
        ├── frr
        └── config
            ├── scenario1
            │   ├── zebra-1.conf
            │   ├── zebra-2.conf
            │   ├── ...
            │
            └── scenario2
                ├── zebra-1.conf
                ├── zebra-2.conf
                ├── ...

The script will create containers which have this workspace folder shared. So you can make any changes you want in FRR, compile and all the changes will immediately be available to all containers, so you only have to get into each byobu and restart daemons in their tabs.

Instructions
------------

Run:

    ./tg.py -f topology.dot

where ```topology.dot is``` the source file containing the topology in DOT format used by GraphViz.

Other available options:

- s: Shell to be used inside byobu (zsh by default)
- w: Workspace base path in host. The place where FRR project and zebra config files are. ```~/workspace``` by default.
- z: Zebra config files folder, relative to container workspace, e.g. ```config/scenario1```. (```test``` by default). Config files must have the name in the form ```${daemon}-${node}.conf```, e.g.: ```zebra-1.conf``` or ```ospfd-3.conf```. You can of course change this manually in the correspondant byobu tab.

A minimal example of a DOT file:

    graph topology {
    1 -- 2
    1 -- 3
    2 -- 4
    3 -- 4
    }

An image of the topology can be generated with graphviz package:

    dot -Tpng topology.dot -o topology.png

You can use ```clean.sh``` script to destroy containers and bridges to be able to run the topology generator again from scratch.
