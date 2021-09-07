# -*- coding: utf-8 -*-
"""
@author: Marcos F. Caetano (mfcaetano@unb.br) 03/11/2020

@description: PyDash Project

An implementation of a MAX POSSIBLE R2A Algorithm.

the quality list is obtained with the parameter of handle_xml_response() method and the choice
is made inside of handle_segment_size_request(), before sending the message down.

In this algorithm the quality choice is always the maximum size possible based
on the last package throughput.
"""

from player.parser import *
from r2a.ir2a import IR2A
import time


class R2AMaxPossible(IR2A):

    def __init__(self, id):
        IR2A.__init__(self, id)
        self.parsed_mpd = ''
        self.qi = []
        self.last_throughput = 0
        self.qi_to_select = len(self.qi) - 1
        self.request_time = 0

    def handle_xml_request(self, msg):
        self.send_down(msg)

    def handle_xml_response(self, msg):
        # getting qi list
        self.parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = self.parsed_mpd.get_qi()
        self.last_throughput = self.qi[-1] + 1
        self.qi_to_select = len(self.qi) - 1

        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        # time to define the segment quality choose to make the request
        self.request_time = time.perf_counter()
        self.qi_to_select = self.select_qi(0, len(self.qi), self.last_throughput) 


        print(f"last_troughput is {self.last_throughput}\nand selected qi is {self.qi[self.qi_to_select]}")
        msg.add_quality_id(self.qi[self.qi_to_select])
        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        self.send_up(msg)
        print(f"qi_to_select: {self.qi_to_select}")
        last_downloaded_size = self.qi[self.qi_to_select]
        self.last_throughput = last_downloaded_size / (time.perf_counter() - self.request_time)

    def initialize(self):
        pass

    def finalization(self):
        pass

    def select_qi(self, l, r, x):
        if r >= l:
            mid = l + (r - l) // 2
            if self.qi[mid] == x:
                return mid
            elif self.qi[mid] > x:
                return self.select_qi(l, mid - 1, x)
            else:
                if len(self.qi) == mid + 1 or self.qi[mid + 1] > x:
                    return mid
                return self.select_qi(mid + 1, r, x)
        else:
            return -1
