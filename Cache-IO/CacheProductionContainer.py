#!/usr/bin/env python3
#
# Author: Kari Vatjus-Anttila <kari.vatjusanttila@gmail.com
#
# For conditions of distribution and use, see copyright notice in LICENSE
#

class CacheProductionContainer():
    def __init__(self):
        self.type = "production"
        self.production_name = ""
        self.production_super_class = ""
        self.description = ""
        self.time_changed = ""
        self.time_created = ""

        # production components
        self.services = []
        self.processes = []
        self.operations = []
        self.external_systems_inbound = []
        self.external_systems_outbound = []

    def __eq__(self, other):
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def getObjectByNameandType(self, name, type):
        for item in self.services:
            if item.name == name and item.type == type:
                return item
        for item in self.processes:
            if item.name == name and item.type == type:
                return item
        for item in self.operations:
            if item.name == name and item.type == type:
                return item
        for item in self.external_systems_inbound:
            if item.name == name and item.type == type:
                return item
        for item in self.external_systems_outbound:
            if item.name == name and item.type == type:
                return item
        return None

    def getObjectByName(self, name):
        for item in self.services:
            if item.name == name:
                return item
        for item in self.processes:
            if item.name == name:
                return item
        for item in self.operations:
            if item.name == name:
                return item
        for item in self.external_systems_inbound:
            if item.name == name:
                return item
        for item in self.external_systems_outbound:
            if item.name == name:
                return item
        return None

    def getObjectById(self, id):
        for item in self.services:
            if item.id == id:
                return item
        for item in self.processes:
            if item.id == id:
                return item
        for item in self.operations:
            if item.id == id:
                return item
        for item in self.external_systems_inbound:
            if item.id == id:
                return item
        for item in self.external_systems_outbound:
            if item.id == id:
                return item
        return None

    def toString(self):
        print("Type: " + self.type.capitalize())
        print("Name: " + self.production_name)
        print("Super Class: " + self.production_super_class)
        print("Description: " + self.description.strip())
        print("Time Changed: " + self.time_changed)
        print("Time Created: " + self.time_created)
        print()
        print("Production Components")
        print("---------------------")
        print("Services:")
        for item in self.services:
            item.toString()
            print()
        print()
        print("Processes:")
        for item in self.processes:
            item.toString()
            print()
        print()
        print("Operations")
        for item in self.operations:
            item.toString()
            print()
        for item in self.external_systems_inbound:
            item.toString()
            print()
        for item in self.external_systems_outbound:
            item.toString()
            print()
        print("---------------------")

class ProductionItem():
    def __init__(self):
        self.name = ""
        self.type = ""
        self.id = ""
        self.class_name = ""
        self.enabled = True
        self.origins = []
        self.originids = []
        self.targets = []
        self.targetids = []
        self.transport = ""
        self.protocol = ""
        self.port = 0
        self.host = ""
        self.sslconfig = ""

    def toString(self):
        print("Name: " + self.name)
        print("Type: " + self.type)
        print("ID: " + str(self.id))
        print("Class Name: " + self.class_name)
        print("Enabled: " + str(self.enabled))
        print("Origins: %s" % ", ".join(map(str, self.origins)))
        print("Targets: %s" % ", ".join(map(str, self.targets)))
        print("Transport: " + self.transport)
        print("Protocol: " + self.protocol)
        print("Port: " + str(self.port))
        print("Hostname: " + self.host)
        print("SSL Config: " + self.sslconfig)