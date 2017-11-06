'''
Created on Oct 12, 2016

@author: mwitt_000
'''
import Queue as queue
import threading
import re
import string

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
    def __init__(self, dg_length, ID, frag_flag, frag_offset, source_addr, dst_addr, data_S):
        self.dg_length = 20 + len(data_S)
        self.ID = ID
        self.frag_flag = frag_flag
        self.frag_offset = frag_offset
        self.source_addr = source_addr
        self.dst_addr = dst_addr
        self.data_S = data_S
        
    ## called when printing the object
    def __str__(self):
        return self.to_byte_S()
        
    ## convert packet to a byte string for transmission over links
    def to_byte_S(self):
        byte_S += self.data_S
        byte_S = str(self.dst_addr).zfill(self.dst_addr_S_length)
        return byte_S
    
    ## extract a packet object from a byte string
    # @param byte_S: byte string representation of the packet
    @classmethod
    def from_byte_S(self, byte_S):
        header = byte_S[0 : 19]
        data_S = byte_S[20 : ]
        return byte_S
    

    

## Implements a network host for receiving and transmitting data
class Host:
    
    packet_count = 0

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
        p = NetworkPacket( 20 + len(data_S),
                           self.packet_count,
                           0,
                           0,
                           self.addr,
                           dst_addr,
                           data_S)
        self.out_intf_L[0].put(p.to_byte_S()) #send packets always enqueued successfully
        print('%s: sending packet "%s" out interface with mtu=%d' % (self, p, self.out_intf_L[0].mtu))
        self.packet_count += 1
        
    ## receive packet from the network layer
    def udt_receive(self):
        pkt_S = self.in_intf_L[0].get()
        if pkt_S is not None:
            print('%s: received packet "%s"' % (self, pkt_S))
       
    ## thread target for the host to keep receiving data
    def run(self):
        print (threading.currentThread().getName() + ': Starting')
        while True:
            #receive data arriving to the in interface
            self.udt_receive()
            #terminate
            if(self.stop):
                print (threading.currentThread().getName() + ': Ending')
                return
        


## Implements a multi-interface router described in class
class Router:
    
# each router may have a different mtu
    max_mtu_size = 40

    def split_message(self, input_string):
        # thanks stack overflow! if only i could just use C instead to split the string up
        return [input_string [i:i+self.max_mtu_size] for i in range(0, len(input_string), self.max_mtu_size)]

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

                    # get the intf numbers from the message
#                    from_intf_num = int(re.findall('^\d+', str(parsed_packet))[0])
#                    print "from_intf_num: " + str(from_intf_num)
#                    to_intf_num = int(re.findall('\d+$', str(parsed_packet))[0])
#                    print "to_intf_num: " + str(to_intf_num)

                    # first 12 bytes are header bytes
                    # the next 4 bytes are the source
                    # next 4 are destination
                    # and then it's just data up to byte
                    # if the total number of those bytes > max_mtu_size, fragmentation needs to occur
                    id = int(parsed_packet[4] + parsed_packet[5])
                    # flag = # get a single bit from a string?
                    # fragmentation_offset =
                    print "PARSED_PACKET = " + parsed_packet
                    source = int(parsed_packet[11] + parsed_packet[12] + parsed_packet[13] + parsed_packet[14]) # the numbers are hard-coded in
                    dest = int(parsed_packet[15] + parsed_packet[16] + parsed_packet[17] + parsed_packet[18], 10)  # b/c it's protocol
                    index = 0
                    pure_data = None
                    for char in parsed_packet:
                        if index >= 19 and parsed_packet != None:
                            pure_data = pure_data + parsed_packet[index]
                            if index == len(parsed_packet):
                                break
                        index += 1
                    #once outside the for loop, all the variables are obtained.
                    #dg id, flag, source, dest, length, message, etc.

                    if len(str(parsed_packet)) > 40:
                        fragmented_message = self.split_message(str(pure_data))
                        print fragmented_message
                    else:
                        self.out_intf_L[i].put(parsed_packet)

# correctlysizedmessage = parsed_packet split by the max_mtu_size
                    correctlysizedmessage = self.split_message(str(parsed_packet))

                    for j in correctlysizedmessage:
                        # put every item in the correctlysizedmessage out interface i
                        self.out_intf_L[i].put(j, True)


                    # HERE you will need to implement a lookup into the 
                    # forwarding table to find the appropriate outgoing interface
                    # for now we assume the outgoing interface is also i
#                    self.out_intf_L[i].put(parsed_packet.to_byte_S(), True)
#                    print('%s: forwarding packet "%s" from interface %d to %d with mtu %d' \
#                        % (self, parsed_packet, i, i, self.out_intf_L[i].mtu))

            except queue.Full:
                print('%s: packet "%s" lost on interface %d' % (self, parsed_packet, i))
                pass
                
    ## thread target for the host to keep forwarding data
    def run(self):
        print (threading.currentThread().getName() + ': Starting')
        while True:
            self.forward()
            if self.stop:
                print (threading.currentThread().getName() + ': Ending')
                return 



