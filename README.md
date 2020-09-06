# vCenter Appliance Simulator

A VMware [vCenter API mock server](https://github.com/vmware/govmomi/tree/master/vcsim") based on [govmomi](https://github.com/vmware/govmomi). This dockerized version provides save defaults for a quick setup. The readme aims to get you started quickly when you need a vCenter API to test your code on.

## Help

To display the supported `vcsim` options just run `docker run omniproc/vcsim -h`, which will override the default container `CMD`.

## Building

If you want to build your own Docker image using this source simply run the following commands:

``` bash
docker build . --build-arg https_proxy=https://http-proxy:8080
docker tag IMAGEID repo/name:version
docker tag IMAGEID repo/name:latest
```

Replace `IMAGEID` with the resulting image hash of the `build` operation. Replace `repo` with your repo name, `name` with the name for the image and `version` with an optional version string for the build. The special version name `latest` enables you to reference the image without specifing a version.

## Starting the mock server

To start the mock server on port 8989 *(default used by vcsim)* simply run the container and specify the container host port to map the container port on *(8989 in this example)*.

``` bash
docker run -p 8989:8989 omniproc/vcsim
```

You can then list the available API methods by opening the [about page](https://127.0.0.1:8989/about) in a browser or crawl them using tools like `curl`:

``` bash
curl -sk https://user:pass@127.0.0.1:8989/about
```

## GOVC

GOVC is bundled in this image to provide a easy client interface for testing VCSIM. If you need to enter the image, use `docker run -it --entrypoint "/bin/bash" omniproc/vcsim`.
Once inside the image you can use the following workflow to get basic information about the simulated environment

``` bash
./vcsim &
export GOVC_URL=https://user:pass@127.0.0.1:8989/sdk GOVC_SIM_PID=YOUR_RETURNED_PID
export GOVC_INSECURE=1

# See https://github.com/vmware/govmomi/blob/master/govc/USAGE.md
./govc -h

./govc about
# Name:         VMware vCenter Server (govmomi simulator)
# Vendor:       VMware, Inc.
# Version:      6.5.0
# Build:        5973321
# OS type:      linux-amd64
# API type:     VirtualCenter
# API version:  6.5
# Product ID:   vpx
# UUID:         dbed6e0c-bd88-4ef6-b594-21283e1c677f

#./govc find -h
./govc find
# /
# /DC0
# /DC0/vm
# /DC0/vm/DC0_H0_VM0
# /DC0/vm/DC0_H0_VM1
# /DC0/vm/DC0_C0_RP0_VM0
# /DC0/vm/DC0_C0_RP0_VM1
# /DC0/host
# /DC0/host/DC0_H0
# /DC0/host/DC0_H0/DC0_H0
# /DC0/host/DC0_H0/Resources
# /DC0/host/DC0_C0
# /DC0/host/DC0_C0/DC0_C0_H0
# /DC0/host/DC0_C0/DC0_C0_H1
# /DC0/host/DC0_C0/DC0_C0_H2
# /DC0/host/DC0_C0/Resources
# /DC0/datastore
# /DC0/datastore/LocalDS_0
# /DC0/network
# /DC0/network/VM Network
# /DC0/network/DVS0
# /DC0/network/DVS0-DVUplinks-9
# /DC0/network/DC0_DVPG0

./govc -i
# Folder:group-d1
# Datacenter:datacenter-2
# Folder:folder-3
# VirtualMachine:vm-51
# VirtualMachine:vm-54
# VirtualMachine:vm-57
# VirtualMachine:vm-60
# Folder:folder-4
# ComputeResource:computeresource-21
# HostSystem:host-19
# ResourcePool:resgroup-20
# ClusterComputeResource:clustercomputeresource-24
# HostSystem:host-30
# HostSystem:host-37
# HostSystem:host-44
# ResourcePool:resgroup-23
# Folder:folder-5
# Datastore:/tmp/govcsim-DC0-LocalDS_0-716203461@folder-5
# Folder:folder-6
# Network:network-7
# DistributedVirtualSwitch:dvs-9
# DistributedVirtualPortgroup:dvportgroup-11
# DistributedVirtualPortgroup:dvportgroup-13

./govc -i /DC0/host/DC0_C0
# ClusterComputeResource:clustercomputeresource-24
# HostSystem:host-30
# VirtualMachine:vm-60
# HostSystem:host-37
# HostSystem:host-44
# VirtualMachine:vm-57
# ResourcePool:resgroup-23

./govc find -i /DC0/host/DC0_C0/DC0_C0_H0
# HostSystem:host-30
# VirtualMachine:vm-60

./govc find -type s
# /DC0/datastore/LocalDS_0
./govc find -i -type s
# Datastore:/tmp/govcsim-DC0-LocalDS_0-716203461@folder-5

./govc vm.info /DC0/vm/DC0_H0_VM0
# Name:           DC0_H0_VM0
# Path:         /DC0/vm/DC0_H0_VM0
# UUID:         98a933c7-e277-4a8d-ab79-c5ad9b772a83
# Guest name:   otherGuest
# Memory:       32MB
# CPU:          1 vCPU(s)
# Power state:  poweredOn
# Boot time:    2018-12-12 07:47:10.7315036 +0000 UTC
# IP address:
# Host:         DC0_H0

./govc device.info -vm /DC0/vm/DC0_H0_VM0 disk-*
# Name:       disk--201-0
#   Type:     VirtualDisk
#   Label:    disk--201-0
#   Summary:  1,024 KB
#   Key:      204
#   File:     [LocalDS_0] DC0_H0_VM0/disk1.vmdk

./govc vm.disk.create -vm /DC0/vm/DC0_H0_VM0 \
-name DC0_H0_VM0/disk2.vmdk \
-ds /DC0/datastore/LocalDS_0 \
-size 10G
# Creating disk

./govc device.info -vm /DC0/vm/DC0_H0_VM0 disk-*
# Name:           disk--201-0
#   Type:         VirtualDisk
#   Label:        disk--201-0
#   Summary:      1,024 KB
#   Key:          204
#   File:         [LocalDS_0] DC0_H0_VM0/disk1.vmdk
# Name:           disk-202-0
#   Type:         VirtualDisk
#   Label:        disk-202-0
#   Summary:      10,485,760 KB
#   Key:          205
#   Controller:   pvscsi-202
#   Unit number:  0
#   File:         [LocalDS_0] DC0_H0_VM0/disk2.vmdk
```

## Testing with PyVmomi

This project has a simple Python test script attached to validate the propper functionality between VCSIM and PyVmomi.
You may see the optional arguments by calling it's help:

``` bash
python .\vcsimtest.py -h
# usage: vcsimtest [-h] [-s HOSTNAME] [-p HOSTPORT] [--nossl] [--debug]
# Test basic VCSIM functionality with PyVmomi.
# optional arguments:
#   -h, --help   show this help message and exit
#   -s HOSTNAME  server hostname of the VCSIM.
#   -p HOSTPORT  server SSL port of the VCSIM.
#   --nossl      disable SSL validation.
#   --debug      enable debug logging.
```
