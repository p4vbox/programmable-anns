#!/usr/bin/env python

#
# Copyright (c) 2015 University of Cambridge
# Copyright (c) 2015 Neelakandan Manihatty Bojan, Georgina Kalogeridou
# All rights reserved.
#
# This software was developed by Stanford University and the University of Cambridge Computer Laboratory
# under National Science Foundation under Grant No. CNS-0855268,
# the University of Cambridge Computer Laboratory under EPSRC INTERNET Project EP/H040536/1 and
# by the University of Cambridge Computer Laboratory under DARPA/AFRL contract FA8750-11-C-0249 ("MRC2"),
# as part of the DARPA MRC research programme.
#
# @NETFPGA_LICENSE_HEADER_START@
#
# Licensed to NetFPGA C.I.C. (NetFPGA) under one or more contributor
# license agreements.  See the NOTICE file distributed with this work for
# additional information regarding copyright ownership.  NetFPGA licenses this
# file to you under the NetFPGA Hardware-Software License, Version 1.0 (the
# "License"); you may not use this file except in compliance with the
# License.  You may obtain a copy of the License at:
#
#   http://www.netfpga-cic.org
#
# Unless required by applicable law or agreed to in writing, Work distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations under the License.
#
# @NETFPGA_LICENSE_HEADER_END@
#
# Author:
#        Modified by Neelakandan Manihatty Bojan, Georgina Kalogeridou

import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

from NFTest import *
import sys, json
import os
#from scapy.layers.all import Ether, IP, TCP
from scapy.all import *

import config_writes

INDEX_WIDTH = 1
if (INDEX_WIDTH > 1):
    REG_DEPTH = 2**INDEX_WIDTH
else:
    REG_DEPTH = INDEX_WIDTH

# read the externs defined in the P4 program
jsonName = 'NNP4_S1'
# EXTERN_DEFINES_FILE = os.path.expandvars('${P4_PROJECT_DIR}/testdata/${P4_PROJECT_NAME}_extern_defines.json')
EXTERN_DEFINES_FILE = os.path.expandvars('${P4_PROJECT_DIR}/testdata/'+jsonName+'_extern_defines.json')
with open(EXTERN_DEFINES_FILE) as f:
    p4_externs = json.load(f)

phy2loop0 = ('../connections/conn', [])
nftest_init(sim_loop = [], hw_config = [phy2loop0])

print "About to start the test"

nftest_start()

def try_read_pkts(pcap_file):
    pkts = []
    try:
        pkts = rdpcap(pcap_file)
    except:
        print pcap_file, ' not found'
    return pkts

def schedule_pkts(pkt_list, iface):
    for pkt in pkt_list:
        pkt.time = baseTime + delta*pkt.time
        pkt.tuser_sport = nf_port_map[iface]

# configure the tables in the P4_SWITCH
nftest_regwrite(0x440200f0, 0x00000001)
nftest_regwrite(0x440200f0, 0x00000001)
nftest_regwrite(0x440200f0, 0x00000001)
nftest_regwrite(0x440200f0, 0x00000001)
nftest_regwrite(0x440200f0, 0x00000001)
config_writes.config_tables()

# Initialize regs to simulate the P4Runtime
# for i in range(REG_DEPTH):
#     nftest_regwrite(p4_externs['switchID']['base_addr'] + i, 1)

proj_dir = os.environ.get('P4_PROJECT_DIR')
nf0_applied  = try_read_pkts(proj_dir + '/testdata/nf0_applied.pcap')
nf1_applied  = try_read_pkts(proj_dir + '/testdata/nf1_applied.pcap')
nf2_applied  = try_read_pkts(proj_dir + '/testdata/nf2_applied.pcap')
nf3_applied  = try_read_pkts(proj_dir + '/testdata/nf3_applied.pcap')
nf0_expected = try_read_pkts(proj_dir + '/testdata/nf0_expected.pcap')
nf1_expected = try_read_pkts(proj_dir + '/testdata/nf1_expected.pcap')
nf2_expected = try_read_pkts(proj_dir + '/testdata/nf2_expected.pcap')
nf3_expected = try_read_pkts(proj_dir + '/testdata/nf3_expected.pcap')

# NOTE: ports are one-hot encoded
nf_port_map = {'nf0':0b00000001, 'nf1':0b00000100, 'nf2':0b00010000, 'nf3':0b01000000}

# send packets after the configuration writes have finished
#baseTime = 1044e-9 + (232e-9)*config_writes.NUM_WRITES #120e-6
baseTime = 20e-6
delta = 1e-6 #1e-8

schedule_pkts(nf0_applied, 'nf0')
schedule_pkts(nf1_applied, 'nf1')
schedule_pkts(nf2_applied, 'nf2')
schedule_pkts(nf3_applied, 'nf3')

# Apply and check the packets
nftest_send_phy('nf0', nf0_applied)
nftest_send_phy('nf1', nf1_applied)
nftest_send_phy('nf2', nf2_applied)
nftest_send_phy('nf3', nf3_applied)
nftest_expect_phy('nf0', nf0_expected)
nftest_expect_phy('nf1', nf1_expected)
nftest_expect_phy('nf2', nf2_expected)
nftest_expect_phy('nf3', nf3_expected)

nftest_barrier()

# for i in range(REG_DEPTH):
#     nftest_regread_expect(p4_externs['buffer']['base_addr'] + i, 0)
# for i in range(REG_DEPTH):
#     nftest_regread_expect(p4_externs['bufferCtr']['base_addr'] + i, 0)
# for i in range(REG_DEPTH):
#     nftest_regread_expect(p4_externs['neuronType']['base_addr'] + i, 0)
# for i in range(REG_DEPTH):
#     nftest_regread_expect(p4_externs['nnID']['base_addr'] + i, 1)
# for i in range(REG_DEPTH):
#     nftest_regread_expect(p4_externs['neuronID']['base_addr'] + i, 0)
# for i in range(REG_DEPTH):
#     nftest_regread_expect(p4_externs['bufferSize']['base_addr'] + i, 1)
# for i in range(REG_DEPTH):
#     nftest_regread_expect(p4_externs['nextLayer']['base_addr'] + i, 14)
# for i in range(REG_DEPTH):
#     nftest_regread_expect(p4_externs['prevLayer']['base_addr'] + i, 0)
# for i in range(REG_DEPTH):
#     nftest_regread_expect(p4_externs['switchID']['base_addr'] + i, 1)

nftest_barrier()

mres=[]
nftest_finish(mres)
