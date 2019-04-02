#!/usr/bin/env python3
#
# Author: Kari Vatjus-Anttila <kari.vatjusanttila@gmail.com
#
# For conditions of distribution and use, see copyright notice in LICENSE
#

import sys, os
import xml.sax
import uuid

import CacheSourceContainer
import CacheProductionContainer

import GraphML_Templates

######
# Description: CacheIO tools used for parsing Caché Objectscript source files and production definitions.
# Outputs an object that can be further processed by some other tools for ex. PlantUML.
#
# One thing to consider is that this implementation relies on the fact that correct metadata
# is added to the production file itself. While using the Management Portal to configure your
# production one should add proper keywords to each component in the form of four keywords (at the moment).
#
# Keyword format: <target/origin system>, <transport>, <protocol>, <component type>.
# e.g. SystemA,TCP/IP,HL7,Service
#
# By using these keywords the I/O tool is able to parse through the production and output a decent graph.
#

class CacheIO():
    def __init__(self, container):
        self.container = container
        self.services_group_id = uuid.uuid4()
        self.processes_group_id = uuid.uuid4()
        self.operations_group_id = uuid.uuid4()
        self.external_inbound_group_id = uuid.uuid4()
        self.external_outbound_group_id = uuid.uuid4()
        self.services_ids = []
        self.processes_ids = []
        self.operations_ids = []
        self.external_inbound_ids = []
        self.external_outbound_ids = []

    # import methods
    def importFromFile(self, filename):
        if self.container.type in "source":
            pass
        elif self.container.type in "production":
            ci = CacheProductionImport(self.container)
        else:
            return
        ci.fromFile(filename)

    # export methods
    def exportPlantUML(self):
        pass

    def exportGraphML(self):
        if self.container is None:
            return
        if self.container.type in "source":
            pass
        elif self.container.type in "production": # lets create a diagram for a production
            document = GraphML_Templates.document_template
            nodes = ""
            edges = ""

            # create nodes
            nodes += self.export_components(self.container.services, "Services", self.services_group_id, self.services_ids)
            nodes += self.export_components(self.container.processes, "Processes", self.processes_group_id, self.processes_ids)
            nodes += self.export_components(self.container.operations, "Operations", self.operations_group_id, self.operations_ids)
            nodes += self.export_components(self.container.external_systems_inbound, "External Systems / Inbound", self.external_inbound_group_id, self.external_inbound_ids)
            nodes += self.export_components(self.container.external_systems_outbound, "External Systems / Outbound", self.external_outbound_group_id, self.external_outbound_ids)
            #nodes += self.export_external_systems(self.container.external_systems, self.external_ids)

            document = document.replace("<NODES_HERE>", nodes)

            edges += self.export_edges(self.container.services)
            edges += self.export_edges(self.container.processes)
            edges += self.export_edges(self.container.operations)
            edges += self.export_edges(self.container.external_systems_inbound)
            edges += self.export_edges(self.container.external_systems_outbound)

            document = document.replace("<EDGES_HERE>", edges)

            with open("output.graphml", "w") as fileOutput:
                fileOutput.write(document)

    def export_components(self, content, group_name, group_id, id_list):
        nodes = ""

        group_node = GraphML_Templates.group_template
        group_node = group_node.replace("<GROUP_CAPTION>", group_name)
        group_node = group_node.replace("<GROUP_ID>", str(group_id))

        for item in content:
            id_list.append(str(item.id))
            node = GraphML_Templates.group_node_template
            node = node.replace("<GROUP_ID>", str(group_id))
            node = node.replace("<NODE_ID>", str(item.id))
            node = node.replace("<NODE_CAPTION>", item.name)
            if nodes == "":
                nodes += node
            else:
                nodes = nodes.replace("<NEXT_NODE>", node)

        nodes = nodes.replace("<NEXT_NODE>", "").strip()
        return group_node.replace("<NODES_HERE>", nodes).strip()

    def export_edges(self, content):
        edges = ""

        for item in content:
            source_node_id = item.id
            other = False
            external = False

            # lookup source id from groups
            if str(source_node_id) in self.services_ids:
                source_node_id = str(self.services_group_id) + "::" + str(source_node_id)
            elif str(source_node_id) in self.processes_ids:
                source_node_id = str(self.processes_group_id) + "::" + str(source_node_id)
            elif str(source_node_id) in self.operations_ids:
                source_node_id = str(self.operations_group_id) + "::" + str(source_node_id)
            elif str(source_node_id) in self.external_inbound_ids:
                source_node_id = str(self.external_inbound_group_id) + "::" + str(source_node_id)
                external = True
            elif str(source_node_id) in self.external_outbound_ids:
                source_node_id = str(self.external_outbound_group_id) + "::" + str(source_node_id)
                external = True
            else:
                other = True

            for node_edge in item.targets:
                if item.type == "Operation":
                    target_node = self.container.getObjectByNameandType(node_edge, "External / Outbound")
                else:
                    target_node = self.container.getObjectByName(node_edge)

                if target_node is None:
                    continue

                target_node_id = ""

                # lookup target id from groups and adjust the id accordingly
                if str(target_node.id) in self.services_ids:
                    target_node_id = str(self.services_group_id) + "::" + str(target_node.id)
                elif str(target_node.id) in self.processes_ids:
                    target_node_id = str(self.processes_group_id) + "::" + str(target_node.id)
                elif str(target_node.id) in self.operations_ids:
                    target_node_id = str(self.operations_group_id) + "::" + str(target_node.id)
                elif str(target_node.id) in self.external_inbound_ids:
                    target_node_id = str(self.external_inbound_group_id) + "::" + str(target_node.id)
                    external = True
                elif str(target_node.id) in self.external_outbound_ids:
                    target_node_id = str(self.external_outbound_group_id) + "::" + str(target_node.id)
                    external = True
                else:
                    other = True

                edge = GraphML_Templates.edge_template
                edge = edge.replace("<EDGE_ID>", str(uuid.uuid4()))
                edge = edge.replace("<SOURCE_NODE>", str(source_node_id))
                edge = edge.replace("<TARGET_NODE>", str(target_node_id))

                if external:
                    edge = edge.replace("<EDGE_CAPTION>", item.transport + " / " + item.protocol)
                else:
                    edge = edge.replace("<EDGE_CAPTION>", "")
                if edges == "":
                    edges += edge
                else:
                    edges = edges.replace("<NEXT_EDGE>", edge)

        return edges.replace("<NEXT_EDGE>", "").strip()

class CacheSourceImport():
    def __init__(self, container):
        self.container = container

    def fromFile(self, filename):
        parser = xml.sax.make_parser()
        cacheparser = CacheSourceImport.XMLParser()
        cacheparser.setCacheContainer(self.container)
        parser.setContentHandler(cacheparser)
        parser.parse(filename)

    class XMLParser(xml.sax.ContentHandler):
        def setCacheContainer(self, container):
            self.container = container

        # start element methods
        def __start_class(self, attributes):
            pass
        def __start_super(self, attributes):
            pass
        def __start_timeChanged(self, attributes):
            pass
        def __start_timeCreated(self, attributes):
            pass
        def __start_parameter(self, attributes):
            pass
        def __start_default(self, attributes):
            pass
        def __start_property(self, attributes):
            pass
        def __start_type(self, attributes):
            pass
        def __start_method(self, attributes):
            pass
        def __start_description(self, attributes):
            pass
        def __start_formalSpec(self, attributes):
            pass
        def __start_returnType(self, attributes):
            pass
        def __start_implementation(self, attributes):
            pass

        # end element methods
        def __end_class(self):
            pass
        def __end_super(self):
            pass
        def __end_timeChanged(self):
            pass
        def __end_timeCreated(self):
            pass
        def __end_parameter(self):
            pass
        def __end_default(self):
            pass
        def __end_property(self):
            pass
        def __end_type(self):
            pass
        def __end_method(self):
            pass
        def __end_description(self):
            pass
        def __end_formalSpec(self):
            pass
        def __end_returnType(self):
            pass
        def __end_implementation(self):
            pass


        def startElement(self, tag, attributes):
            if tag == "Class":              return self.__start_class(attributes)
            if tag == "Super":              return self.__start_super(attributes)
            if tag == "TimeChanged":        return self.__start_timeChanged(attributes)
            if tag == "TimeCreated":        return self.__start_timeCreated(attributes)
            if tag == "Parameter":          return self.__start_parameter(attributes)
            if tag == "Default":            return self.__start_default(attributes)
            if tag == "Property":           return self.__start_property(attributes)
            if tag == "Type":               return self.__start_type(attributes)
            if tag == "Method":             return self.__start_method(attributes)
            if tag == "Description":        return self.__start_description(attributes)
            if tag == "FormalSpec":         return self.__start_formalSpec(attributes)
            if tag == "ReturnType":         return self.__start_returnType(attributes)
            if tag == "Implementation":     return self.__start_implementation(attributes)

        def endElement(self, tag):
            if tag == "Class":              return self.__end_class()
            if tag == "Super":              return self.__end_super()
            if tag == "TimeChanged":        return self.__end_timeChanged()
            if tag == "TimeCreated":        return self.__end_timeCreated()
            if tag == "Parameter":          return self.__end_parameter()
            if tag == "Default":            return self.__end_default()
            if tag == "Property":           return self.__end_property()
            if tag == "Type":               return self.__end_type()
            if tag == "Method":             return self.__end_method()
            if tag == "Description":        return self.__end_description()
            if tag == "FormalSpec":         return self.__end_formalSpec()
            if tag == "ReturnType":         return self.__end_returnType()
            if tag == "Implementation":     return self.__end_implementation()


class CacheProductionImport():
    def __init__(self, container):
        self.container = container

    def fromFile(self, filename):
        # step 1: parse contents of the file to get class names and other useful information about the production
        parser = xml.sax.make_parser()
        cacheparser = CacheProductionImport.XMLParser()
        cacheparser.setCacheContainer(self.container)
        parser.setContentHandler(cacheparser)
        parser.parse(filename)

        # step 2: parse contents of the cdata block containing the production definition
        payload = cacheparser.getPayload()
        cacheparser = CacheProductionImport.ProductionParser()
        cacheparser.setCacheContainer(self.container)
        xml.sax.parseString(payload, cacheparser)

    class XMLParser(xml.sax.ContentHandler):
        superclass = False
        timeChanged = False
        timeCreated = False
        cdata = False
        data_read = False

        # contains data inside <Data> block
        payload = ""

        def setCacheContainer(self, container):
            self.container = container

        def getPayload(self):
            return self.payload

        # start element methods
        def __start_class(self, attributes):
            if self.data_read: return
            self.container.production_name = str(attributes.getValueByQName("name"))
        def __start_super(self, attributes):
            if self.data_read: return
            self.superclass = True

        def __start_timeChanged(self, attributes):
            if self.data_read: return
            self.timeChanged = True

        def __start_timeCreated(self, attributes):
            if self.data_read: return
            self.timeCreated = True

        def __start_data(self, attributes):
            if self.data_read: return
            self.cdata = True

        # end element methods
        def __end_class(self):
            self.data_read = True
            self.classname = False

        def __end_super(self):
            self.superclass = False

        def __end_timeChanged(self):
            self.timeChanged = False

        def __end_timeCreated(self):
            self.timeCreated = False

        def __end_data(self):
            self.cdata = False

        def startElement(self, tag, attributes):
            if tag == "Class":              return self.__start_class(attributes)
            if tag == "Super":              return self.__start_super(attributes)
            if tag == "TimeChanged":        return self.__start_timeChanged(attributes)
            if tag == "TimeCreated":        return self.__start_timeCreated(attributes)
            if tag == "Data":               return self.__start_data(attributes)

        def endElement(self, tag):
            if tag == "Class":              return self.__end_class()
            if tag == "Super":              return self.__end_super()
            if tag == "TimeChanged":        return self.__end_timeChanged()
            if tag == "TimeCreated":        return self.__end_timeCreated()
            if tag == "Data":               return self.__end_data()

        def characters(self, content):
            if self.superclass:
                self.container.production_super_class += content
            if self.timeChanged:
                self.container.time_changed += content
            if self.timeCreated:
                self.container.time_created += content
            if self.cdata:
                self.payload += content

    class ProductionParser(xml.sax.ContentHandler):
        # general flags when a specific tag is found
        production = True
        description = True
        item = True

        # flags used when parsing Settings for a given Item
        targetconfignameFound = False
        webserviceurlFound = False
        httpportFound = False
        httpserverFound = False
        portFound = False
        sslconfigFound = False
        responseFromFound = False

        def setCacheContainer(self, container):
            self.container = container
            self.productionitem = None

        # start element methods
        def __start_production(self, attributes):
            self.production = True

        def __start_description(self, attributes):
            self.description = True

        def __start_item(self, attributes):
            self.item = True
            self.productionitem = CacheProductionContainer.ProductionItem()
            self.productionitem.id = uuid.uuid4()
            categories = str(attributes.getValueByQName("Category"))

            # populate production item
            self.productionitem.name = str(attributes.getValueByQName("Name"))
            self.productionitem.class_name = str(attributes.getValueByQName("ClassName"))

            if "Service" in categories:
                self.productionitem.type = "Service"
            elif "Process" in categories:
                self.productionitem.type = "Process"
            elif "Operation" in categories:
                self.productionitem.type = "Operation"

            # if above failed for some reason or another lets try one last attempt to discover the item type
            if self.productionitem.type is "":
                if ".BS." in self.productionitem.class_name or ".Service." in self.productionitem.class_name:
                    self.productionitem.type = "Service"
                elif ".BP." in self.productionitem.class_name or ".Process." in self.productionitem.class_name:
                    self.productionitem.type = "Process"
                elif ".BO." in self.productionitem.class_name or ".Operation." in self.productionitem.class_name:
                    self.productionitem.type = "Operation"

            categories = categories.split(",")

            if str(attributes.getValueByQName("Enabled")) in "true":
                self.productionitem.enabled = True
            else:
                self.productionitem.enabled = False

            if self.productionitem.type in "Service":
                try: self.productionitem.origins.append(categories[0])
                except: pass
                try: self.productionitem.transport = categories[1]
                except: self.productionitem.transport = "N/A"
                try: self.productionitem.protocol = categories[2]
                except: self.productionitem.protocol = "N/A"
                # Service is at the edge. Origin describes the contacting external service
                if self.container.getObjectByNameandType(categories[0], "External / Inbound") is None:
                    externalitem = CacheProductionContainer.ProductionItem()
                    externalitem.type = "External / Inbound"
                    externalitem.id = uuid.uuid4()
                    externalitem.targets.append(self.productionitem.id)
                    try: externalitem.name = categories[0]
                    except: externalitem.name = "Unknown Service"
                    try: externalitem.transport = categories[1]
                    except: externalitem.transport = "N/A"
                    try: externalitem.protocol = categories[2]
                    except: externalitem.protocol = "N/A"
                    self.container.external_systems_inbound.append(externalitem)
                else:
                    self.container.getObjectByNameandType(categories[0], "External / Inbound").targets.append(self.productionitem.id)
            elif self.productionitem.type in "Operation":
                try: self.productionitem.targets.append(categories[0])
                except: pass
                try: self.productionitem.transport = categories[1]
                except: self.productionitem.transport = "N/A"
                try: self.productionitem.protocol = categories[2]
                except: self.productionitem.protocol = "N/A"
                # Operation is at the edge of the production. Target describes the external service that the operation contacts)
                if self.container.getObjectByNameandType(categories[0], "External / Outbound") is None:
                    externalitem = CacheProductionContainer.ProductionItem()
                    externalitem.type = "External / Outbound"
                    externalitem.id = uuid.uuid4()
                    externalitem.origins.append(self.productionitem.id)
                    try: externalitem.name = categories[0]
                    except: externalitem.name = "Unknown Service"
                    try: externalitem.transport = categories[1]
                    except: externalitem.transport = "N/A"
                    try: externalitem.protocol = categories[2]
                    except: externalitem.protocol = "N/A"
                    self.container.external_systems_outbound.append(externalitem)
                else:
                    self.container.getObjectByNameandType(categories[0], "External / Outbound").origins.append(self.productionitem.id)

        def __start_setting(self, attributes):
            if attributes.getValueByQName("Name") in "TargetConfigName":
                self.targetconfignameFound = True
            elif attributes.getValueByQName("Name") in "WebServiceURL":
                self.webserviceurlFound = True
            elif attributes.getValueByQName("Name") in "HTTPPort":
                self.httpportFound = True
            elif attributes.getValueByQName("Name") in "HTTPServer":
                self.httpserverFound = True
            elif attributes.getValueByQName("Name") in "Port":
                self.portFound = True
            elif attributes.getValueByQName("Name") in "SSLConfig":
                self.sslconfigFound = True
            elif attributes.getValueByQName("Name") in "ResponseFrom":
                self.responseFromFound = True

        # end element methods
        def __end_production(self):
            self.production = False

        def __end_description(self):
            self.description = False

        def __end_item(self):
            if self.item:
                if self.productionitem.type in "Service":
                    self.container.services.append(self.productionitem)
                elif self.productionitem.type in "Process":
                    self.container.processes.append(self.productionitem)
                elif self.productionitem.type in "Operation":
                    self.container.operations.append(self.productionitem)
                self.productionitem = None
                self.item = False

        def __end_setting(self):
            pass

        def startElement(self, tag, attributes):
            if tag == "Production":         return self.__start_production(attributes)
            if tag == "Description":        return self.__start_description(attributes)
            if tag == "Item":               return self.__start_item(attributes)
            if tag == "Setting":            return self.__start_setting(attributes)

        def endElement(self, tag):
            if tag == "Production":         return self.__end_production()
            if tag == "Description":        return self.__end_description()
            if tag == "Item":               return self.__end_item()
            if tag == "Setting":            return self.__end_setting()

        def characters(self, content):
            if self.description:
                self.container.description += content
            elif self.targetconfignameFound:
                self.productionitem.targets.append(content)
                self.targetconfignameFound = False
            elif self.webserviceurlFound:
                if self.productionitem.host is "":
                    try:
                        self.productionitem.port = content.split("/")[2].split(":")[1]
                        self.productionitem.host = content.split("/")[2].split(":")[0]
                    except:
                        if content.split("/")[0].lower() in "http:":
                            self.productionitem.port = 80
                        elif content.split("/")[0].lower() in "https:":
                            self.productionitem.port = 443
                        self.productionitem.host = content.split("/")[2]
                self.webserviceurlFound = False
            elif self.httpportFound:
                if self.productionitem.port is 0:
                    self.productionitem.port += int(content)
                self.httpportFound = False
            elif self.httpserverFound:
                if self.productionitem.host is "":
                    self.productionitem.host += content
                self.httpserverFound = False
            elif self.portFound:
                if self.productionitem.port is 0:
                    self.productionitem.port += int(content)
                self.portFound = False
            elif self.sslconfigFound:
                if self.productionitem.sslconfig is "":
                    self.productionitem.sslconfig += content
                self.sslconfigFound = False
            elif self.responseFromFound:
                for item in content.split(","):
                    self.productionitem.targets.append(item)
                self.responseFromFound = False