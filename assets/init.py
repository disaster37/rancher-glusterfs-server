#!/usr/bin/python
import os
from gluster.Gluster import Gluster
import sys
import time
from rancher_metadata import MetadataAPI

__author__ = 'Sebastien LANGOUREAUX'


class ServiceRun():

  def __init__(self, service_name, gluster_directory, list_volumes, transport, stripe = None, replica = None, quota = None):
    """ Init gluster
    """


    if service_name is None or service_name == "":
      raise Exception("You must set the service name")
    if gluster_directory is None or gluster_directory == "":
      raise Exception("You must set te directory to store gluster folume")
    if transport is None or transport == "":
      raise Exception("You must set the transport")

    self.__service_name = service_name
    self.__gluster_directory = gluster_directory
    self.__list_volumes = list_volumes
    self.__transport = transport
    self.__stripe = stripe
    self.__replica = replica
    self.__quota = quota
    self.__is_on_cluster = False

  def run(self):

    print("Wait 120s that glusterfs start and another node also start \n")
    time.sleep(120)

    while True:
        try:
            self.manage_cluster()
        except Exception,e:
            print("Some error appear : " + e.message)

        time.sleep(300)




  def manage_cluster(self):
    gluster = Gluster()
    peer_manager = gluster.get_peer_manager()
    volume_manager = gluster.get_volume_manager()
    metadata_manager = MetadataAPI()

    # I check there are more than 1 container
    number_node = metadata_manager.get_service_scale_size()
    if number_node < 2 :
        print("You must scale this service (2 or more containers)")
        return False

        
    # I get my container info
    my_name = metadata_manager.get_container_name()
    my_ip = metadata_manager.get_container_ip()
    my_id = metadata_manager.get_container_id()


    # I get the other container info
    list_containers = {}
    list_containers_name = metadata_manager.get_service_containers()
    is_scale_complet = True
    for container_name in list_containers_name:
        if container_name != my_name:
            list_containers[container_name] = {}
            list_containers[container_name]['id'] = metadata_manager.get_container_id(container_name)
            list_containers[container_name]['name'] = container_name
            list_containers[container_name]['ip'] = metadata_manager.get_container_ip(container_name)
            if list_containers[container_name]['ip'] is None or list_containers[container_name]['ip'] == '':
                is_scale_complet = False
                print("The container " + container_name + " have not yet the IP")



    # Then I look if I am already on cluster
    peer_status = peer_manager.status()
    if peer_status["peers"] == 0:
        print("I am " + my_name + " and my IP is " + my_ip)
        print("There are " + str(number_node) + " container is this service")
        print("I am not yet on cluster")

        # Now I look if there are already cluster
        is_cluster_found = False
        for container in list_containers.itervalues():
            if container['ip'] is not None and container['ip'] != '':
                gluster_temp = Gluster(container['ip'])
                peer_status = gluster_temp.get_peer_manager().status()
                if peer_status["peers"] > 0:
                    is_cluster_found = True
                    break

        if is_cluster_found is True:
            print("There are  already cluster. I will wait that member guest him")
            return True

        # No yet cluster
        else:
            if is_scale_complet == False:
                print("There are no cluster. I wait some time that the service start all container before create it.")
                return False

            print("There are no cluster. I will get if I am the master")
            isMaster = True

            # Now I loop on all node to compar my score
            for container in list_containers.itervalues():
                if container['id'] < my_id:
                    isMaster = False
                    break

            # I am slave
            if isMaster == False:
                print("I am a slave and I am not yet on cluster. I sleep and I wait the master guest me on cluster")
                return True

            # I am the master
            print("I will create the new cluster")
            if (number_node % int(self.__replica)) != 0 :
                print("The number of node is not compatible with your replica number. It must be a multiple of " + str(self.__replica) + ". We do nothink while the number is not compatible.")
                return False


            for container in list_containers.itervalues():
                peer_manager.probe(container['ip'])
                print(container['name'] +  " ( " + container['ip'] + " ) " + " added on cluster")


             # Stay all node that join the cluster before create all volumes
            print("Wait all node join the cluster .")
            while number_node != metadata_manager.get_service_scale_size():
                print(".")
                time.sleep(5)
            # Now I create the volume
            print("I will create all volumes")


            for volume in self.__list_volumes:
                list_bricks = []
                for container in list_containers.itervalues():
                    list_bricks.append(container['ip'] + ':' + self.__gluster_directory + '/' + volume)

                list_bricks.append( my_ip + ':' + self.__gluster_directory + '/' + volume)

                volume_manager.create(volume, list_bricks, self.__transport, self.__stripe, self.__replica, self.__quota)
                print("Volume '" + volume + "' has been created")

            return True

    # Look if I must guest ne node
    elif peer_status["peers"] < number_node:
        print("New container detected")
        # Check if number is compatible with replica
        if (number_node % int(self.__replica)) != 0:
            print("The number of node is not compatible with your replica number. It must be a multiple of " + str(self.__replica) + ". I do nothink while the number is not compatible")
            return False

        list_node = []
        for container in list_containers.itervalues():
            if container['ip'] not in peer_status["host"]:
                peer_manager.probe(container['ip'])
                print(container['name'] +  " ( " + container['ip'] + " ) " + " added on cluster")
                list_node.append(container['ip'])

        # Stay all node that join the cluster before create all volumes
        print("Wait all node join the cluster .")
        while number_node != metadata_manager.get_service_scale_size():
            print(".")
            time.sleep(5)
        # Now I extend the existing volume
        print("I will extend all volume without change replica")
        for volume in self.__list_volumes:
            list_bricks = []
            for node_ip in list_node:
                list_bricks.append(node_ip + ':' + self.__gluster_directory + '/' + volume)

            volume_manager.extend(volume, list_bricks, self.__replica)
            print("Volume '" + volume + "' has been extented")

        return True

    return True



if __name__ == '__main__':
    # Start
    if(len(sys.argv) > 1 and sys.argv[1] == "start"):

        service = ServiceRun(os.getenv('SERVICE_NAME'), os.getenv('GLUSTER_DATA'), os.getenv('GLUSTER_VOLUMES').split(','), os.getenv('GLUSTER_TRANSPORT'), os.getenv('GLUSTER_STRIPE'), os.getenv('GLUSTER_REPLICA'), os.getenv('GLUSTER_QUOTA'))
        service.run()


