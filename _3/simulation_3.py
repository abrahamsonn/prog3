'''
Created on Oct 12, 2016

@author: mwitt_000
'''
import network_3
import link_3
import threading
from time import sleep

##configuration parameters
router_queue_size = 0 # 0 means unlimited
simulation_time =   1 # give the network sufficient time to transfer all packets before quitting

if __name__ == '__main__':
    object_L = [] #keeps track of objects, so we can kill their threads
    
    #create network nodes
    client1 = network_3.Host(1)
    object_L.append(client1)
    client2 = network_3.Host(2)
    object_L.append(client2)
    server3 = network_3.Host(3)
    object_L.append(server3)
    server4 = network_3.Host(4)
    object_L.append(server4)
    
    convergingRoutingTable = {'0001' : 0, '0002' : 1}
    singleRouteRoutingTable = {'0001' : 0, '0002' : 0}
    
    router_a = network_3.Router(name='A', intf_count=2, max_queue_size=router_queue_size, routingTable=convergingRoutingTable)
    object_L.append(router_a)
    router_b = network_3.Router(name='B', intf_count=1, max_queue_size=router_queue_size, routingTable=singleRouteRoutingTable)
    object_L.append(router_b)
    router_c = network_3.Router(name='C', intf_count=1, max_queue_size=router_queue_size, routingTable=singleRouteRoutingTable)
    object_L.append(router_c)
    router_d = network_3.Router(name='D', intf_count=2, max_queue_size=router_queue_size, routingTable=convergingRoutingTable)
    object_L.append(router_d)
    # object_L = an object list
    
    #create a Link Layer to keep track of links between network nodes
    link_layer = link_3.LinkLayer()
    object_L.append(link_layer)
    
    #add all the links
    link_layer.add_link(link_3.Link(client1, 0, router_a, 0, 40))
    link_layer.add_link(link_3.Link(client2, 0, router_a, 1, 40))
    link_layer.add_link(link_3.Link(router_a, 0, router_b, 0, 40))
    link_layer.add_link(link_3.Link(router_a, 1, router_c, 0, 40))
    link_layer.add_link(link_3.Link(router_b, 0, router_d, 0, 40))
    link_layer.add_link(link_3.Link(router_c, 0, router_d, 1, 40))
    link_layer.add_link(link_3.Link(router_d, 0, server3, 0, 40))
    link_layer.add_link(link_3.Link(router_d, 1, server4, 0, 40))
    
    
    #start all the objects
    thread_L = []
    thread_L.append(threading.Thread(name=client1.__str__(), target=client1.run))
    thread_L.append(threading.Thread(name=client2.__str__(), target=client2.run))
    thread_L.append(threading.Thread(name=server3.__str__(), target=server3.run))
    thread_L.append(threading.Thread(name=server4.__str__(), target=server4.run))
    thread_L.append(threading.Thread(name=router_a.__str__(), target=router_a.run))
    thread_L.append(threading.Thread(name=router_b.__str__(), target=router_b.run))
    thread_L.append(threading.Thread(name=router_c.__str__(), target=router_c.run))
    thread_L.append(threading.Thread(name=router_d.__str__(), target=router_d.run))
    
    thread_L.append(threading.Thread(name="Network", target=link_layer.run))
    
    for t in thread_L:
        t.start()
    
    
    #create some send events    
    #for i in range(3):
    client1.udt_send(3, 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse feugiat, mauris amet.')
    client2.udt_send(4, 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse feugiat, mauris amet.')
    
    
    #give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)
    
    #join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()
        
#    print("All simulation threads joined")



# writes to host periodically
