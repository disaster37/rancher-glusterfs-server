# Table of Contents
- [Introduction](#introduction)
    - [Version](#version)
    - [Changelog](Changelog.md)
- [Hardware Requirements](#hardware-requirements)
    - [CPU](#cpu)
    - [Memory](#memory)
    - [Storage](#storage)
- [Contributing](#contributing)
- [Issues](#issues)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
  - [ACCESS](#access)
  - [QUEUE](#queue)
  - [TOPIC](#topic)
  - [Data Store](#data-store)
  - [BROKER](#broker)
  - [Disk usage](#disk-usage)
  - [JMX](#JMX)
  - [Avaible Configuration Parameters](#avaible-configuration-parameters)
  - [Advance configuration](#advance-configuration)
- [References](#references)

# Introduction

Docker container that lauch Glusterfs server. It's dedicated to work on Rancher environment and use auto discovery service to create the initial cluster and auto extented it in the next time.

## Version

Current Version: **0.1.0**

# Hardware Requirements

## CPU

- No stats avaible to say the number of core that you need for the size of your storage

## Memory

- No stats avaible to say the memory that you need for the size of your storage
- I think add some guster option to allow the setting some cache on memory

## Storage

The storage determine the size of your potential volume. It's depend of the number of volume and the number of replica.
If you create many volume, and you should that volume can't take more space, you can use environment varibale "GLUSTER_QUOTA".
By default, all data are store on '/data'. So it's good idea to add volume on it. You can also setting this with 'GLUSTER_DATA' environment variable.

# Contributing

If you find this image useful here's how you can help:

- Send a Pull Request with your awesome new features and bug fixes
- Help new users with [Issues](https://github.com/disaster37/rancher-glusterfs-server/issues) they may encounter
- Send me a tip via [Bitcoin](https://www.coinbase.com/disaster37) or using [Gratipay](https://gratipay.com/disaster37/)


# Quick Start
Like I have say at the beginning, this container work only on Rancher plateform. On your stack (applications), create new service (Add Service).

## Main section
- NAME : Put 'gluster' as a name of your service. If you change this name, you must add environment variable name SERVICE_NAME with the name of your current service.
- SCALE:  Run 2 or more container. I think you can start with 2 and upgrade later with 4 if needed
- SELECT IMAGE : put 'webcenter/rancher-glusterfs-server:latest'

## ADVANCED OPTIONS - Command
- ENVIRONMENT VARS : put the environment variable that you need to custom Glusterfs
  - SERVICE_NAME : it' the name of you service. By default it's 'gluster'
  - GLUSTER_DATA : It's path to store glusterfs data. By default it's '/data'
  - GLUSTER_VOLUMES : It's the list of volume you need to host on the glusterfs (for exemple : 'dbvol,appvol'). By default it's 'ranchervol'.
  - GLUSTER_TRANSPORT : It's the transport on glusterfs. By default it's 'tcp'.
  - GLUSTER_REPLICA : It's the number of replica for your data hosted on gluster. By default it's '2'.
  - GLUSTER_STRIPE : It's the stripe of your volume . By default it's disable.
  - GLUSTER_QUOTA : It's the quota size for your each volume (for exemple '10GB'): By default it's disable.

## ADVANCED OPTIONS - Volumes
  - VOLUMES : Put '/data' on your host. For exemple : '/data/MY_STACK:/data'

## ADVANCED OPTIONS - Security/Host
  - CAPABILITIES : Add 'SYS_ADMIN'. It's needed lauchn glusterfs
  - DEVICE BINDING : Put '/dev/fuse'. It's needed by glusterfs (for exemple if you use quota)

## ADVANCED OPTIONS - Scheduling
  - Add scheduling with the following rules : 'The host must not have a service with the name 'MY_STACK/gluster'. This rules permit to lauchn a unique container gluster of this stack on each host (it's better to avoid SPOF).




