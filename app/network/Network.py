import sumolib
import random
from random import randrange

from app import Config
from app.routing.RoutingEdge import RoutingEdge

import os, sys

# import of SUMO_HOME
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


class Network(object):
    """ simply ready the network in its raw form and creates a router on this network """

    # empty references to start with
    edges = None
    nodes = None
    nodeIds = None
    edgeIds = None
    routingEdges = None
    sourceNodeIds = []      # 2d array holds array of source nodes ids used for generating traffic from specific source
    targetNodeIds = []      # same as above but for target : Note: element of this array should be equal to the elemenet of sourceNodeId. len(sourceNodeIds) == len(targetNodeIds)

    @classmethod
    def loadNetwork(cls):
        """ loads the network and applies the results to the Network static class """
        # parse the net using sumolib
        parsedNetwork = sumolib.net.readNet(Config.sumoNet)
        # apply parsing to the network
        Network.__applyNetwork(parsedNetwork)

    @classmethod
    def __applyNetwork(cls, net):
        """ internal method for applying the values of a SUMO map """
        cls.nodeIds = map(lambda x: x.getID(), net.getNodes())  # type: list[str]
        cls.edgeIds = map(lambda x: x.getID(), net.getEdges())  # type: list[str]
        cls.nodes = net.getNodes()
        cls.edges = net.getEdges()
        cls.routingEdges = map(lambda x: RoutingEdge(x), net.getEdges())
        #assigning network functions to class instance
        cls.getNeighboringLanes = net.getNeighboringLanes
        cls.getNeighboringEdges = net.getNeighboringEdges
        cls.getLaneFromId = net.getLane
        # Below two arrays are used to hold node ids which are used for traffic flow from source to target ids
        if Config.restrictTrafficFlow == True:
            s, t = Config.trafficSource, Config.trafficTarget
            allSourceEdges = cls.getEdgesFromPositionArray(s)
            allTargetEdges = cls.getEdgesFromPositionArray(t)
            for se in allSourceEdges:
                cls.sourceNodeIds.append(map(lambda x : Network.getEdgeIDsToNode(x[0].getID()).getID(), se))
            for te in allTargetEdges:
                cls.targetNodeIds.append(map(lambda x : Network.getEdgeIDsToNode(x[0].getID()).getID(), te))

    @classmethod
    def getEdgesFromPositionArray(cls, arr):
        "concatinate all edges retrieved from position and radius"
        edgeArr = []
        for x in range(len(arr)):
            edgesFromPos = map(lambda x: Network.getEdgeFromPosition(x[0], x[1], x[2]),  arr[x])
            allEdges = []
            for i in edgesFromPos:
                for j in i:
                    allEdges.append(j)
            edgeArr.append(allEdges)
        return edgeArr

    @classmethod
    def nodesCount(cls):
        """ count the nodes """
        return len(cls.nodes)

    @classmethod
    def edgesCount(cls):
        """ count the edges """
        return len(cls.edges)

    @classmethod
    def getEdgeFromNode(cls, edge):
        return edge.getFromNode()

    @classmethod
    def getEdgeByID(cls, edgeID):
        return [x for x in cls.edges if x.getID() == edgeID][0]

    @classmethod
    def getEdgeIDsToNode(cls, edgeID):
        return cls.getEdgeByID(edgeID).getToNode()

    # returns the edge position of an edge
    @classmethod
    def getPositionOfEdge(cls, edge):
        return edge.getFromNode().getCoord()  # @todo average two

    # get edge from x and y cordinates of the map
    @classmethod
    def getEdgeFromPosition(cls, x, y, r):
        return cls.getNeighboringEdges(x, y, r)

    # this method was created to generate source and target of the cars 
    # that will be from the pool or nodes at one side of the map to the
    # other side of the map.
    # i.e can be used to make the flow of traffic from one area to the other area in the map
    @classmethod
    def getDefinedSourceTargetNodeIds(cls):
        randIndex = randrange(len(cls.sourceNodeIds))
        return random.choice(cls.sourceNodeIds[randIndex]), random.choice(cls.targetNodeIds[randIndex])