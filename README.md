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




