FROM webcenter/rancher-stack-base:latest
MAINTAINER Sebastien LANGOUREAUX <linuxworkgroup@hotmail.com>


ENV SERVICE_NAME "gluster"
ENV GLUSTER_DATA "/data"
ENV GLUSTER_VOLUMES "ranchervol"
ENV GLUSTER_TRANSPORT "tcp"
ENV GLUSTER_STRIPE 1
ENV GLUSTER_REPLICA 2

# Use it if you should put some quota on your volume
#ENV GLUSTER_QUOTA "10GB"


RUN apt-get update && \
    apt-get install -y glusterfs-server


RUN mkdir /data

# Install python lib to manage glusterfs
WORKDIR /usr/src
RUN git clone https://github.com/disaster37/python-gluster.git
WORKDIR /usr/src/python-gluster
RUN python setup.py install

# Add some script to init the glusterfs cluster
ADD assets/setup/supervisor-glusterfs.conf /etc/supervisor/conf.d/glusterfs.conf
ADD assets/init.py /app/


VOLUME ["${GLUSTER_DATA}", "/var/lib/glusterd" ]


# CLEAN APT
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
