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
import sys
import os
#from scapy.layers.all import Ether, IP, TCP
from scapy.all import *

import config_writes

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
baseTime = 10e-6
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

nftest_regread_expect(0x44030000, 0x00000001)
nftest_regread_expect(0x44030000, 0x00000001)
nftest_regread_expect(0x44030000, 0x00000001)
nftest_regread_expect(0x44030000, 0x00000001)
nftest_regread_expect(0x44030000, 0x00000001)
nftest_regread_expect(0x44030000, 0x00000001)
nftest_regread_expect(0x44030000, 0x00000001)
nftest_regread_expect(0x44030000, 0x00000001)
nftest_regread_expect(0x44030000, 0x00000001)
# Simulating the CLI table commands
# remove entry
# nftest_regwrite(0x44020050, 0x11111108)
# nftest_regwrite(0x44020054, 0x00000811)
# nftest_regread_expect(0x44020044, 0x00000001)
# nftest_regwrite(0x44020040, 0x00000002)
# nftest_regread_expect(0x44020044, 0x00000001)
# nftest_regread_expect(0x44020044, 0x00000001)
# # add entry
# nftest_regwrite(0x44020050, 0x11111108)
# nftest_regwrite(0x44020054, 0x00000811)
# nftest_regwrite(0x44020080, 0x00000101)
# nftest_regread_expect(0x44020044, 0x00000001)
# nftest_regwrite(0x44020040, 0x00000001)
# nftest_regread_expect(0x44020044, 0x00000001)
# nftest_regread_expect(0x44020044, 0x00000001)
# # get size
# nftest_regread_expect(0x44020024, 0x00000009)
# # read entry
# nftest_regwrite(0x44020050, 0x11111108)
# nftest_regwrite(0x44020054, 0x00000811)
# nftest_regread_expect(0x44020044, 0x00000001)
# nftest_regwrite(0x44020040, 0x00000003)
# nftest_regread_expect(0x44020044, 0x00000001)
# nftest_regread_expect(0x44020044, 0x00000001)
# nftest_regread_expect(0x44020080, 0x00000101)
# nftest_regread_expect(0x44020048, 0x00000001)


mres=[]
nftest_finish(mres)
