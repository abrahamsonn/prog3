'''
Created on Oct 12, 2016

@author: mwitt_000
'''
import Queue as queue
import threading
import re

## wrapper class for a queue of packets
class Interface:
    ## @param maxsize - the maximum size of the queue storing packets
    def __init__(self, maxsize=0):
        self.queue = queue.Queue(maxsize);
        self.mtu = None
    
    ##get packet from the queue interface
    def get(self):
        try:
            return self.queue.get(False)
        except queue.Empty:
            return None
        
    ##put the packet into the interface queue
    # @param pkt - Packet to be inserted into the queue
    # @param block - if True, block until room in queue, if False may throw queue.Full exception
    def put(self, pkt, block=False):
        self.queue.put(pkt, block)
        
## Implements a network layer packet (different from the RDT packet 
# from programming assignment 2).
# NOTE: This class will need to be extended to for the packet to include
# the fields necessary for the completion of this assignment.
class NetworkPacket:
    ## packet encoding lengths 
    dst_addr_S_length = 5
    
    ##@param dst_addr: address of the destination host
    # @param data_S: packet payload
    def __init__(self, data_S):
        self.complete_string = data_S
        self.dst_addr = data_S[16 : 20]
        self.source = data_S[12 : 16]
        self.header = data_S[0 : 19]
        self.data_S = data_S[20 : ]


    ## called when printing the object
    def __str__(self):
        return self.to_byte_S()
        
    ## convert packet to a byte string for transmission over links
    def to_byte_S(self):
        byte_S = str(self.dst_addr).zfill(self.dst_addr_S_length)
        byte_S += self.data_S
        return self.complete_string
    
    ## extract a packet object from a byte string
    # @param byte_S: byte string representation of the packet
    @classmethod
    def from_byte_S(self, byte_S):
        dst_addr = int(byte_S[0 : NetworkPacket.dst_addr_S_length])
        data_S = byte_S[19 : ]
        return byte_S
    

    

## Implements a network host for receiving and transmitting data
class Host:

    packet_count = 1

    ##@param addr: address of this node represented as an integer
    def __init__(self, addr):
        self.addr = addr
        self.in_intf_L = [Interface()]
        self.out_intf_L = [Interface()]
        self.stop = False #for thread termination
    
    ## called when printing the object
    def __str__(self):
        return 'Host_%s' % (self.addr)
       
    ## create a packet and enqueue for transmission
    # @param dst_addr: destination address for the packet
    # @param data_S: data being transmitted to the network layer
    def udt_send(self, dst_addr, data_S):
        full_datagram = str(len(data_S)).zfill(4)\
                        + str(self.packet_count).zfill(2)\
                        + "00"\
                        + "0000"\
                        + str(self.addr).zfill(4)\
                        + str(dst_addr).zfill(4)\
                        + str(data_S)
        p = NetworkPacket(full_datagram)
        print 'Host_%s sending packet "%s"\n\n' % (self.addr, p.to_byte_S())
        self.out_intf_L[0].put(p.to_byte_S()) #send packets always enqueued successfully

        self.packet_count += 1

    ## receive packet from the network layer
    def udt_receive(self):
        pkt_S = self.in_intf_L[0].get()
        if pkt_S != None:
            print('%s: received packet "%s"' % (self, pkt_S))
            return pkt_S
       
    ## thread target for the host to keep receiving data
    def run(self):
#print (threading.currentThread().getName() + ': Starting')
        firstMessage = []
        secondMessage = []
        thirdMessage = []
        while True:
            #receive data arriving to the in interface
            x = self.udt_receive()
            if x != None:
                id = int(x[4:6])
                pos = int(x[6:8]) / 20
                if id == 1:
                    # print "pos = " + str(pos)
                    firstMessage.insert(pos, x[20: ])
                if id == 2:
                    secondMessage.insert(pos, x[20: ])
                if id == 3:
                    thirdMessage.insert(pos, x[20: ])
            #terminate
            if(self.stop):
                if len(firstMessage) != 0:
                    print "First Message: = " + ''.join(firstMessage)
                if len(secondMessage) != 0:
                    print "Second Message: = " + ''.join(secondMessage)
                if len(thirdMessage) != 0:
                    print "Third Message: = " + ''.join(thirdMessage)
#print (threading.currentThread().getName() + ': Ending')
                return
        


## Implements a multi-interface router described in class
class Router:

    max_mtu_size = 40

    def split_message(self, input_string):
        # thanks stack overflow! if only i could just use C instead
        message_length = len(input_string)
        if message_length <= 20:
            print "Empty message foo"
            return None
        else:
            dst_addr = input_string[16: 20]
            source = input_string[12: 16]
            header = input_string[0 : 19]
            message = input_string[20 : ]
            # return [ input_string [ i : i + self.max_mtu_size] for i in range(19, message_length), self.max_mtu_size]
            # each message fragment should be max_mtu_size - 20 characters in length ( - 20 so that each can have a header)
            # fragments = [input_string [i:i+self.max_mtu_size] for i in range(19, message_length), self.max_mtu_size]
            fragments = [input_string [i:i+self.max_mtu_size] for i in range(0, message_length, self.max_mtu_size)]
            #print fragments
            return fragments

        # return [input_string [i:i+self.max_mtu_size] for i in range(0, len(input_string), self.max_mtu_size)]

    ##@param name: friendly router name for debugging
    # @param intf_count: the number of input and output interfaces 
    # @param max_queue_size: max queue length (passed to Interface)
    def __init__(self, name, intf_count, max_queue_size):
        self.stop = False #for thread termination
        self.name = name
        #create a list of interfaces
        self.in_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]
        self.out_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]

    ## called when printing the object
    def __str__(self):
        return 'Router_%s' % (self.name)

    ## look through the content of incoming interfaces and forward to
    # appropriate outgoing interfaces
    def forward(self):
        for i in range(len(self.in_intf_L)):
            pkt_S = None

            try:
                # pkt_S = packet received from interface i
                pkt_S = self.in_intf_L[i].get()
                #if packet exists make a forwarding decision
                if pkt_S is not None:

                    parsed_packet = NetworkPacket.from_byte_S(pkt_S) #parse a packet out
#                     # get the intf numbers from the message
#                     from_intf_num = int(re.findall('^\d+', str(parsed_packet))[0])
# #                    if from_intf_num != None:
# #                        print "from_intf_num: " + str(from_intf_num)
#
#                     to_intf_num = int(re.findall('\d+$', str(parsed_packet))[0])
# #                    if to_intf_num != None:
# #                        print "to_intf_num: " + str(to_intf_num)

                    # ID = str(parsed_packet[4]) + str(parsed_packet[5])
                    ID = parsed_packet[4:6]
                    #print "ID: " + str(ID)
                    dst_addr = parsed_packet[16: 20]
                    source = parsed_packet[12: 16]
                    header = parsed_packet[0: 19]
                    message = parsed_packet[20:]

                    if len(parsed_packet) > self.max_mtu_size:
                        pure_message = parsed_packet[20 : ]
                        correctlysizedmessage = self.split_message(str(pure_message))
                        # "correctlysizedmessage" + str(correctlysizedmessage)
                        index = 0
                        for fragment in correctlysizedmessage:
                            well_formed_datagram = str(len(fragment)).zfill(4) + \
                                                   str(ID).zfill(2) + \
                                                   str((self.max_mtu_size - 20) * index).zfill(2) + \
                                                   '0000' + \
                                                   str(source).zfill(4) + \
                                                   str(dst_addr).zfill(4) + \
                                                   fragment
                            print "WFD: " + well_formed_datagram + "\n\n"
                            self.out_intf_L[i].put(well_formed_datagram, True)

                            index += 1

                    else:
                        print "From " + str(source) + " to " + str(dst_addr) + ":"
                        print message
                        self.out_intf_L[i].put(parsed_packet, True)


                    # HERE you will need to implement a lookup into the 
                    # forwarding table to find the appropriate outgoing interface
                    # for now we assume the outgoing interface is also i
#                    self.out_intf_L[i].put(parsed_packet.to_byte_S(), True)
#                    print('%s: forwarding packet "%s" from interface %d to %d with mtu %d' \
#                        % (self, parsed_packet, i, i, self.out_intf_L[i].mtu))

            except queue.Full:
#                print('%s: packet "%s" lost on interface %d' % (self, parsed_packet, i))
                pass
                
    ## thread target for the host to keep forwarding data
    def run(self):
#        print (threading.currentThread().getName() + ': Starting')
        while True:
            self.forward()
            if self.stop:
#                print (threading.currentThread().getName() + ': Ending')
                return 



