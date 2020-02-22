
from PyQt5 import QtWidgets, QtCore, QtGui

from Katana import UI4, NodegraphAPI, Utils, GeoAPI, Nodes3DAPI, FnGeolib, FnAttribute

import os
import json


class Utils(object):
    ''' GLOBAL UTILS '''
    def cookLocation(self, node, scenegraph_loc):
        #  =====================================================
        # helper function to get attributes on a SG loc
        # returns the client cooked location
        #  =====================================================
        runtime = FnGeolib.GetRegisteredRuntimeInstance()
        txn = runtime.createTransaction()

        client = txn.createClient()
        op = Nodes3DAPI.GetOp(txn, node)
        txn.setClientOp(client, op)
        runtime.commit(txn)
        location = client.cookLocation(scenegraph_loc)
        return location, client

    def getGlobalAttr(self, client, path, attrName):
        #  =====================================================
        # tests to see if an attribute exists or not, if it does it exist,
        # it will return the Attr and the Location of the attr
        #  =====================================================
        if not path:
            return None, None

        location = client.cookLocation(path)
        attr = location.getAttrs().getChildByName(attrName)
        if attr:
            return attr, path
        else:
            parent = '/'.join(path.split('/')[:-1])
            return self.getGlobalAttr(client, parent, attrName)

    def getGlobalAttrString(self, location=None, attr_loc=None, node=None):
        '''
        @location: <str> scenegraph location
        @attr_loc: <str> attribute location
        @node: node to resolve on
        '''
        client = self.cookLocation(node, location)[1]
        #  ---------------------------------- global attrs
        attr = self.getGlobalAttr(
            client,
            location,
            attr_loc)[0]
        if attr:
            nearest_sample = attr.getNearestSample(0)
            if attr.getNumberOfValues() == 3:
                value = ' '.join([str(x) for x in nearest_sample])
            elif attr.getNumberOfValues() == 1:
                value = str(attr.getValue())
            else:
                # this is for arrays... probably
                value = ''
        else:
            value = '<Invalid>'

        return value

    def resetParametersDataType(
            self,
            meta_data=None,
            widget_type_data=None,
            node=None,
            reset_list=None
        ):
        '''
        @reset_list: <list> of strings with Scenegraph Locations to be reset
        @meta_data: <AbstractItem>
        @widget_type_data: <dict> widget data
        '''
        # ===================================================================
        # Update Parameters
        #
        # Basically this nasty thing here goes through and deletes the old
        # value parameter, and then creates a new one with the correct
        # data type... please note that this will reset all user values back
        # to default
        # ===================================================================
        def updateParam(location):
            value_group_param = value_param.getChild('value')
            if value_group_param:
                value_param.deleteChild(value_param.getChild('value'))
                parent_location = location[:location.rindex('/')]
                value = self.getGlobalAttrString(
                    location=parent_location,
                    attr_loc=attr_loc,
                    node=update_node
                )

                if value == '<Invalid>':
                    value = self.getGlobalAttrString(
                        location=location,
                        attr_loc=attr_loc,
                        node=update_node
                    )

                if value:
                    if data_type == 'color':
                        default_value = value.split(' ')
                        new_param = value_param.createChildGroup('value')
                        try:
                            red = new_param.createChildNumber('red', float(default_value[0]))
                            green = new_param.createChildNumber('green', float(default_value[1]))
                            blue = new_param.createChildNumber('blue', float(default_value[2]))
                        except:
                            red = new_param.createChildNumber('red', 0)
                            green = new_param.createChildNumber('green', 0)
                            blue = new_param.createChildNumber('blue', 0)
                    else:
                        new_param = value_param.createChildString('value', '%s'%value)
                    update_node.flushAll()

        if node:
            if meta_data:
                widget_type_data = meta_data.getWidgetTypeData()
            data_type = widget_type_data['data_type']
            if data_type != '':
                attr_loc = widget_type_data['attr_loc']

                update_node_name = node.getParameter('nodeReference.update_node').getValue(0)
                update_node = NodegraphAPI.GetNode(update_node_name)
                user_param = update_node.getParameter('user')
                for child in user_param.getChildren():
                    current_attr_loc = child.getChild('attr_loc').getValue(0)
                    if current_attr_loc == attr_loc:
                        value_group = child.getChild('value')
                        for value_param in value_group.getChildren():
                            location = value_param.getChild('location').getValue(0)
                            if reset_list:
                                if location in reset_list:
                                    updateParam(location)
                            else:
                                updateParam(location)

    def loadHotkeys(self):
        file_name = os.path.dirname(os.path.realpath(__file__)) + '/Preferences/HOTKEYS.json'
        if file_name:
            with open(file_name, 'r') as f:
                #datastore = json.load(f)
                HOTKEYS=json.load(f)
                return HOTKEYS