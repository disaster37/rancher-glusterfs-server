#!/usr/bin/python
import os
import subprocess
from threading import Thread
from gluster.Gluster import Gluster
import sys
import time
import socket

__author__ = 'Sebastien LANGOUREAUX'


class ThreadGluster(Thread):

  def __init__(self, service_name, gluster_directory, list_volumes, transport, stripe = None, replica = None, quota = None):
    """ Init gluster
    """


    if service_name is None or service_name == "":
      raise Exception("You must set the service name")
    if gluster_directory is None or gluster_directory == "":
      raise Exception("You must set te directory to store gluster folume")
    if transport is None or transport == "":
      raise Exception("You must set the transport")

    Thread.__init__(self)
    self.__service_name = service_name
    self.__gluster_directory = gluster_directory
    self.__list_volumes = list_volumes
    self.__transport = transport
    self.__stripe = stripe
    self.__replica = replica
    self.__quota = quota

  def run(self):

    print("Wait 60s that glusterfs start and another node also start \n")
    time.sleep(60)

    while True:
        self.manage_cluster()
        time.sleep(300)




  def manage_cluster(self):
    gluster = Gluster()
    peer_manager = gluster.get_peer_manager()
    volume_manager = gluster.get_volume_manager()

    # First, check if I am the master. The master is the smallest IP that returned by 'dig SERVICE_NAME'
    program = ["/usr/bin/dig",
        self.__service_name,
        '+short'
        ]
    try:
        response = subprocess.check_output(program).split("\n")
        if len(response) == 0:
            print("No dns answer for service name '" + self.__service_name + "'. Are you sure is the name of your service ? Else set the '-e SERVICE_NAME' with the good value")
            sys.exit(1)
        elif len(response) == 1:
            print("I am alone. So I can't create the glusterfs cluster")
            sys.exit(1)
        else:
            print("There are " + len(response) + " servers. Now I will look if I am the master")
    except subprocess.CalledProcessError,e:
        print("Some errors appear when I dig the service name : " + e.output)
        sys.exit(1)

    # Now I get my IP to look if I am the master
    my_ip = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1]
    if my_ip is None:
        print("I can't found my IP")
        sys.exit(1)

    print("My IP is " + my_ip + ". I will get my score and compare to another node")
    my_score = int(my_ip.replace('.',''))
    isMaster = True

    # Now I loop on all node to compar my score
    for node_ip in response:
        if node_ip != my_ip:
            node_score = int(my_ip.replace('.',''))
            if node_score < my_score:
                isMaster = False
                break
    # I am slave
    if isMaster == False:
        peer_status = peer_manager.status()
        if peer_status["peers"] == 0:
            print("I am a slave and I am not yet on cluster. I sleep and I wait the master meet me on cluster")
        else:
            print("I am a slave and I am already on cluster. I sleep")

        return True

    # I am the master
    print("I am the master")
    peer_status = peer_manager.status()

    # Cluster not yet created
    if peer_status["peers"] == 0:
        list_node = []
        print("I create the new cluster")
        for node_ip in response:
            peer_manager.probe(node_ip)
            print(node_ip + " added on cluster")
            list_node.append(node_ip)



        # Now I create the volume
        list_bricks = []
        print("I create all volume")
        for volume in self.__list_volumes:
            for node_ip in list_node:
                list_bricks.append(node_ip + ':' + self.__gluster_directory + '/' + volume)
            volume_manager.create(volume, list_bricks, self.__transport, self.__stripe, self.__replica, self.__quota)
            print("Volume '" + volume + "' has been created")

        return True

    # New node
    elif peer_status["peers"] < len(response):
        print("New container detected")
        list_node = []
        for node_ip in response:
            if node_ip not in peer_status["host"]:
                peer_manager.probe(node_ip)
                print(node_ip + "added on cluster")
                list_node.append(node_ip)

        # Now I extend the existing volume
        list_bricks = []
        print("I extend all volume")
        for volume in self.__list_volumes:
            for node_ip in list_node:
                list_bricks.append(node_ip + ':' + self.__gluster_directory + '/' + volume)
            volume_manager.extend(volume, list_bricks, self.__replica)
            print("Volume '" + volume + "' has been extented")


        return True


    print("do nothink")
    return True



if __name__ == '__main__':
    # Start
    if(len(sys.argv) > 1 and sys.argv[1] == "start"):

        thread_gluster = ThreadGluster(os.getenv('SERVICE_NAME'), os.getenv('GLUSTER_DATA'), os.getenv('GLUSTER_VOLUMES').split(','), os.getenv('GLUSTER_TRANSPORT'), os.getenv('GLUSTER_STRIPE'), os.getenv('GLUSTER_REPLICA'), os.getenv('GLUSTER_QUOTA'))
        thread_gluster.start()

        # Start services
        os.system("/usr/bin/supervisord -n -c /etc/supervisor/supervisord.conf")
