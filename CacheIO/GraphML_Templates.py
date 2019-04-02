#!/usr/bin/env python3
#
# Author: Kari Vatjus-Anttila <kari.vatjusanttila@gmail.com
#
# For conditions of distribution and use, see copyright notice in license.txt
#

######
# Document Template: Replace the following tags for relevant information
# <NODES_HERE>: Field that should be replaced at least with one node_template
# <EDGES_HERE>: Field that should be replaced with one edge_template if edges are present
#
document_template = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns" xmlns:java="http://www.yworks.com/xml/yfiles-common/1.0/java" xmlns:sys="http://www.yworks.com/xml/yfiles-common/markup/primitives/2.0" xmlns:x="http://www.yworks.com/xml/yfiles-common/markup/2.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:y="http://www.yworks.com/xml/graphml" xmlns:yed="http://www.yworks.com/xml/yed/3" xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://www.yworks.com/xml/schema/graphml/1.1/ygraphml.xsd">
  <!--Created by yEd 3.17.2-->
  <key attr.name="Description" attr.type="string" for="graph" id="d0"/>
  <key for="port" id="d1" yfiles.type="portgraphics"/>
  <key for="port" id="d2" yfiles.type="portgeometry"/>
  <key for="port" id="d3" yfiles.type="portuserdata"/>
  <key attr.name="url" attr.type="string" for="node" id="d4"/>
  <key attr.name="description" attr.type="string" for="node" id="d5"/>
  <key for="node" id="d6" yfiles.type="nodegraphics"/>
  <key for="graphml" id="d7" yfiles.type="resources"/>
  <key attr.name="url" attr.type="string" for="edge" id="d8"/>
  <key attr.name="description" attr.type="string" for="edge" id="d9"/>
  <key for="edge" id="d10" yfiles.type="edgegraphics"/>
  <graph edgedefault="directed" id="G">
    <data key="d0"/>
    <NODES_HERE>
    <EDGES_HERE>
  </graph>
  <data key="d7">
    <y:Resources/>
  </data>
</graphml>
"""

######
# Node Template: Replace the following tags for relevant information
# <NODE_ID>: Unique ID for this node
# <NODE_CAPTION>: Caption for this node
# <NEXT_NODE>: Remove this tag if this is the final node. Otherwise this can be used to append another node using this template
#
node_template = """<node id="<NODE_ID>">
      <data key="d4"/>
      <data key="d5"/>
      <data key="d6">
        <y:UMLClassNode>
          <y:Geometry height="28.0" width="100.0" x="646.0" y="195.0"/>
          <y:Fill color="#FFCC00" transparent="false"/>
          <y:BorderStyle color="#000000" type="line" width="1.0"/>
          <y:NodeLabel alignment="center" autoSizePolicy="content" fontFamily="Dialog" fontSize="13" fontStyle="bold" hasBackgroundColor="false" hasLineColor="false" height="19.92626953125" horizontalTextPosition="center" iconTextGap="4" modelName="custom" textColor="#000000" verticalTextPosition="bottom" visible="true" width="38.68994140625" x="30.655029296875" y="3.0"><NODE_CAPTION><y:LabelModel>
              <y:SmartNodeLabelModel distance="4.0"/>
            </y:LabelModel>
            <y:ModelParameter>
              <y:SmartNodeLabelModelParameter labelRatioX="0.0" labelRatioY="0.0" nodeRatioX="0.0" nodeRatioY="0.0" offsetX="0.0" offsetY="0.0" upX="0.0" upY="-1.0"/>
            </y:ModelParameter>
          </y:NodeLabel>
          <y:UML clipContent="true" constraint="" omitDetails="false" stereotype="" use3DEffect="true">
            <y:AttributeLabel/>
            <y:MethodLabel/>
          </y:UML>
        </y:UMLClassNode>
      </data>
    </node>
    <NEXT_NODE>
"""

######
# Edge Template: Replace the following tags for relevant information
# <EDGE_ID>: Unique ID for this edge
# <SOURCE_NODE>: Source node ID
# <TARGET_NODE>: Target node ID
# <EDGE_CAPTION>: Caption for this edge
# <NEXT_EDGE>: Remove this tag if this is the final edge. Otherwise this can be used to append another edge using this template
#
edge_template = """<edge id="<EDGE_ID>" source="<SOURCE_NODE>" target="<TARGET_NODE>">
      <data key="d9"/>
      <data key="d10">
        <y:PolyLineEdge>
          <y:Path sx="0.0" sy="0.0" tx="0.0" ty="0.0"/>
          <y:LineStyle color="#000000" type="line" width="1.0"/>
          <y:Arrows source="none" target="standard"/>
          <y:EdgeLabel alignment="center" configuration="AutoFlippingLabel" distance="2.0" fontFamily="Dialog" fontSize="12" fontStyle="plain" hasBackgroundColor="false" hasLineColor="false" height="18.701171875" horizontalTextPosition="center" iconTextGap="4" modelName="custom" preferredPlacement="anywhere" ratio="0.5" textColor="#000000" verticalTextPosition="bottom" visible="true" width="26.013671875" x="70.97216796875" y="20.6494140625"><EDGE_CAPTION><y:LabelModel>
              <y:SmartEdgeLabelModel autoRotationEnabled="false" defaultAngle="0.0" defaultDistance="10.0"/>
            </y:LabelModel>
            <y:ModelParameter>
              <y:SmartEdgeLabelModelParameter angle="0.0" distance="30.0" distanceToCenter="true" position="right" ratio="0.5" segment="0"/>
            </y:ModelParameter>
            <y:PreferredPlacementDescriptor angle="0.0" angleOffsetOnRightSide="0" angleReference="absolute" angleRotationOnRightSide="co" distance="-1.0" frozen="true" placement="anywhere" side="anywhere" sideReference="relative_to_edge_flow"/>
          </y:EdgeLabel>
          <y:BendStyle smoothed="false"/>
        </y:PolyLineEdge>
      </data>
    </edge>
    <NEXT_EDGE>
"""

######
# Group Template: Replace the following tags for relevant information
# <GROUP_ID>
# <GROUP_CAPTION>
# <NODES_HERE>
#
group_template = """

<node id="<GROUP_ID>" yfiles.foldertype="group">
  <data key="d4"/>
  <data key="d5"/>
  <data key="d6">
    <y:ProxyAutoBoundsNode>
      <y:Realizers active="0">
        <y:GroupNode>
          <y:Geometry height="258.3765873015873" width="130.0" x="-15.0" y="-258.3765873015873"/>
          <y:Fill color="#F5F5F5" transparent="false"/>
          <y:BorderStyle color="#000000" type="dashed" width="1.0"/>
          <y:NodeLabel alignment="right" autoSizePolicy="node_width" backgroundColor="#EBEBEB" borderDistance="0.0" fontFamily="Dialog" fontSize="15" fontStyle="plain" hasLineColor="false" height="22.37646484375" horizontalTextPosition="center" iconTextGap="4" modelName="internal" modelPosition="t" textColor="#000000" verticalTextPosition="bottom" visible="true" width="130.0" x="0.0" y="0.0"><GROUP_CAPTION></y:NodeLabel>
          <y:Shape type="roundrectangle"/>
          <y:State closed="false" closedHeight="50.0" closedWidth="50.0" innerGraphDisplayEnabled="false"/>
          <y:Insets bottom="15" bottomF="15.0" left="15" leftF="15.0" right="15" rightF="15.0" top="15" topF="15.0"/>
          <y:BorderInsets bottom="1" bottomF="1.0" left="0" leftF="0.0" right="0" rightF="0.0" top="1" topF="1.0001224578372785"/>
        </y:GroupNode>
        <y:GroupNode>
          <y:Geometry height="50.0" width="50.0" x="0.0" y="60.0"/>
          <y:Fill color="#F5F5F5" transparent="false"/>
          <y:BorderStyle color="#000000" type="dashed" width="1.0"/>
          <y:NodeLabel alignment="right" autoSizePolicy="node_width" backgroundColor="#EBEBEB" borderDistance="0.0" fontFamily="Dialog" fontSize="15" fontStyle="plain" hasLineColor="false" height="22.37646484375" horizontalTextPosition="center" iconTextGap="4" modelName="internal" modelPosition="t" textColor="#000000" verticalTextPosition="bottom" visible="true" width="59.02685546875" x="-4.513427734375" y="0.0">Folder 1</y:NodeLabel>
          <y:Shape type="roundrectangle"/>
          <y:State closed="true" closedHeight="50.0" closedWidth="50.0" innerGraphDisplayEnabled="false"/>
          <y:Insets bottom="5" bottomF="5.0" left="5" leftF="5.0" right="5" rightF="5.0" top="5" topF="5.0"/>
          <y:BorderInsets bottom="0" bottomF="0.0" left="0" leftF="0.0" right="0" rightF="0.0" top="0" topF="0.0"/>
        </y:GroupNode>
      </y:Realizers>
    </y:ProxyAutoBoundsNode>
  </data>
  <graph edgedefault="directed" id="<GROUP_ID>:">
  <NODES_HERE>
  </graph>
</node>
"""

#####
# Group Node Template: Replace the following tags for relevant information
# <GROUP_ID>
# <NODE_ID>
# <NODE_CAPTION>
# <NEXT_NODE>
#
group_node_template = """
<node id="<GROUP_ID>::<NODE_ID>">
  <data key="d4"/>
  <data key="d5"/>
  <data key="d6">
    <y:UMLClassNode>
      <y:Geometry height="28.0" width="100.0" x="0.0" y="-220.0"/>
      <y:Fill color="#FFCC00" transparent="false"/>
      <y:BorderStyle color="#000000" type="line" width="1.0"/>
      <y:NodeLabel alignment="center" autoSizePolicy="content" fontFamily="Dialog" fontSize="13" fontStyle="bold" hasBackgroundColor="false" hasLineColor="false" height="19.92626953125" horizontalTextPosition="center" iconTextGap="4" modelName="custom" textColor="#000000" verticalTextPosition="bottom" visible="true" width="38.68994140625" x="30.655029296875" y="3.0"><NODE_CAPTION><y:LabelModel>
          <y:SmartNodeLabelModel distance="4.0"/>
        </y:LabelModel>
        <y:ModelParameter>
          <y:SmartNodeLabelModelParameter labelRatioX="0.0" labelRatioY="0.0" nodeRatioX="0.0" nodeRatioY="0.0" offsetX="0.0" offsetY="0.0" upX="0.0" upY="-1.0"/>
        </y:ModelParameter>
      </y:NodeLabel>
      <y:UML clipContent="true" constraint="" omitDetails="false" stereotype="" use3DEffect="true">
        <y:AttributeLabel/>
        <y:MethodLabel/>
      </y:UML>
    </y:UMLClassNode>
  </data>
</node>
<NEXT_NODE>
"""