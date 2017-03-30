FROM debian:jessie

ENV HOME /root

RUN DEBIAN_FRONTEND=noninteractive apt-get update -yqq && \
    apt-get install -yqq --no-install-recommends \
    net-tools \
    aptitude \
    less \
    openssh-server \
    libxml-libxml-perl \
    libc-ares-dev \
    bison \
    flex \
    libjson-c-dev \
    byobu \
    zsh \
    bridge-utils \
    ethtool && \
    rm -rf /var/lib/apt/lists/*

ADD utils/.zshrc $HOME
ADD utils/zaliasrc $HOME
ADD utils/.zsh $HOME/.zsh

ADD utils/rename_iface.sh $HOME
RUN chmod +x $HOME/rename_iface.sh

# ssh key
RUN mkdir -p $HOME/.ssh
ADD utils/container_rsa.pub /tmp
RUN cat /tmp/container_rsa.pub >> $HOME/.ssh/authorized_keys

#$HOME/workspace
#VOLUME $CONTAINER_WORKSPACE_PATH
#WORKDIR $CONTAINER_WORKSPACE_PATH

ADD utils/byobu_container.sh $HOME
RUN chmod +x $HOME/byobu_container.sh

CMD service ssh restart && tail -f /dev/null
