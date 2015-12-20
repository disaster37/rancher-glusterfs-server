#!/usr/bin/python
import os
from gluster.Gluster import Gluster
import sys
import time
from rancher_metadata import MetadataAPI

__author__ = 'Sebastien LANGOUREAUX'


class ServiceRun():

  def __init__(self, gluster_directory, list_volumes, transport, stripe = None, replica = None, quota = None):
    """ Init gluster
    """


    if gluster_directory is None or gluster_directory == "":
      raise Exception("You must set te directory to store gluster folume")
    if transport is None or transport == "":
      raise Exception("You must set the transport")

    self.__gluster_directory = gluster_directory
    self.__list_volumes = list_volumes
    self.__transport = transport
    self.__stripe = stripe
    self.__replica = replica
    self.__quota = quota
    self.__is_on_cluster = False



  def __is_already_on_glusterfs(self):
    gluster = Gluster()
    peer_manager = gluster.get_peer_manager()
    peer_status = peer_manager.status()
    if peer_status["peers"] == 0:
        return False
    else:
        return True

  def __is_cluster_already_exist(self, list_nodes):
    for node in list_nodes.itervalues():
        gluster = Gluster(node['ip'])
        peer_status = gluster.get_peer_manager().status()
        if peer_status["peers"] > 0:
            return True

    return False

  def __wait_all_glusterfs_start(self, list_nodes):

      loop = True
      while loop:
        time.sleep(1)
        try:
            for node in list_nodes.itervalues():
                gluster = Gluster(node['ip'])
                peer_status = gluster.get_peer_manager().status()

            loop = False
        except Exception,e:
            loop = True



  def __create_all_volumes(self, list_volumes, transport, stripe, replica, quota, directory, list_nodes):
    gluster = Gluster()
    volume_manager = gluster.get_volume_manager()

    for volume in list_volumes:
        try:
            volume_manager.info(volume)
        except Exception,e:
            if e.message.find("Volume " + volume +" does not exist") >= 0:
                list_bricks = []
                for node in list_nodes.itervalues():
                    list_bricks.append(node['ip'] + ':' + directory + '/' + volume)
                volume_manager.create(volume, list_bricks, transport, stripe, replica, quota)
                print("Volume '" + volume + "' has been created")
            else:
                raise e


  def __create_cluster(self, list_nodes, numbers_nodes):
    gluster = Gluster()
    peer_manager = gluster.get_peer_manager()
    for node in list_nodes.itervalues():
        peer_manager.probe(node['ip'])
        print(node['name'] +  " ( " + node['ip'] + " ) " + " added on cluster")

    # I wait all node join the glusterfs before continue
    while(self.__get_numbers_peer() != numbers_nodes):
        time.sleep(1)

  def __get_numbers_peer(self):
    gluster = Gluster()
    peer_manager = gluster.get_peer_manager()
    peer_status = peer_manager.status()

    return peer_status["peers"]


  def __get_peers(self):
    gluster = Gluster()
    peer_manager = gluster.get_peer_manager()
    return peer_manager.status()

  def __get_my_container_info(self):
    metadata_manager = MetadataAPI()
    current_container = {}
    current_container["name"] = metadata_manager.get_container_name()
    current_container["ip"] = metadata_manager.get_container_ip()
    current_container["id"] = metadata_manager.get_container_id()

    return current_container


  def __get_other_container_in_service(self, my_name):
    metadata_manager = MetadataAPI()
    list_containers = {}
    list_containers_name = metadata_manager.wait_service_containers()
    for container_name in list_containers_name:
        if container_name != my_name:
            list_containers[container_name] = {}
            list_containers[container_name]['id'] = metadata_manager.get_container_id(container_name)
            list_containers[container_name]['name'] = container_name
            list_containers[container_name]['ip'] = metadata_manager.get_container_ip(container_name)


    return list_containers


  def __get_numbers_of_node_in_service(self):
      metadata_manager = MetadataAPI()
      return metadata_manager.get_service_scale_size()


  def _is_master(self, current_container, list_containers):

    for container in list_containers.itervalues():
        if container['id'] < current_container["id"]:
            return False

    return True



  def run(self):

    current_container = self.__get_my_container_info()
    list_containers = self.__get_other_container_in_service(current_container)

    print("Wait all glusterfs start on all node : ")
    self.__wait_all_glusterfs_start(list_containers)
    print("Ok \n")

    while True:
        try:
            self.manage_cluster()
        except Exception,e:
            print("Some error appear : " + e.message)
            print("I will try again in 60s")

        time.sleep(60)




  def manage_cluster(self):
    gluster = Gluster()
    peer_manager = gluster.get_peer_manager()
    volume_manager = gluster.get_volume_manager()
    metadata_manager = MetadataAPI()

    # I check there are more than 1 container
    number_node = self.__get_numbers_of_node_in_service()

    # I get my container info
    current_container = self.__get_my_container_info()

    # I get all other containers
    list_containers = self.__get_other_container_in_service(current_container["name"])

    # If I am not on cluster and there are no cluster and I am the master, so I create the gluster
    if (self.__is_already_on_glusterfs() is False) and (self._is_master(current_container, list_containers) is True) and (self.__is_cluster_already_exist(list_containers) is False):
        self.__create_cluster(list_containers, number_node)



    # If I am already on cluster and there are new peer, I guest them.
    if (self.__is_already_on_glusterfs() is True) and (number_node > self.__get_numbers_peer()):

        list_nodes = {}
        peer_status = self.__get_peers()
        for container in list_containers.itervalues():
            if container['ip'] not in peer_status["host"]:
                list_nodes[container["name"]] = container
                print("New host : " + container["name"])


        self.__create_cluster(list_nodes, number_node)
        list_containers = list_nodes


    # I create all volumes
    if self.__is_already_on_glusterfs() is True:
        list_nodes = list_containers.copy()
        list_nodes[current_container["name"]] = current_container
        self.__create_all_volumes(self.__list_volumes, self.__transport, self.__stripe, self.__replica, self.__quota,self.__gluster_directory,list_nodes)




if __name__ == '__main__':
    # Start


    service = ServiceRun(os.getenv('GLUSTER_DATA'), os.getenv('GLUSTER_VOLUMES').split(','), os.getenv('GLUSTER_TRANSPORT'), os.getenv('GLUSTER_STRIPE'), os.getenv('GLUSTER_REPLICA'), os.getenv('GLUSTER_QUOTA'))
    service.run()
