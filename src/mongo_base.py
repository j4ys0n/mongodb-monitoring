#!/usr/bin/env python

from abc import abstractmethod
import pymongo, json

from bson import json_util
from splunklib.modularinput import Script, Argument
from splunklib.modularinput.event import Event


class MongoScript(Script):

    def to_json(self, obj):
        return json.dumps(obj, default=json_util.default)

    def create_event(self, input_name, sourcetype, obj):
        event = Event()
        event.stanza = input_name
        event.sourceType = sourcetype
        event.data = self.to_json(obj)
        return event

    def get_scheme(self):
        scheme = self.create_scheme()
        scheme.use_external_validation = True
        host_argument = Argument("server")
        host_argument.title = "Host"
        host_argument.data_type = Argument.data_type_string
        host_argument.description = "hostname or IP address of the instance to connect to, or a mongodb URI, or a list of hostnames/mongodb URIs"
        host_argument.required_on_create = True
        scheme.add_argument(host_argument)
        port_argument = Argument("port")
        port_argument.title = "Port"
        port_argument.data_type = Argument.data_type_string
        port_argument.description = "port number on which to connect"
        port_argument.required_on_create = True
        scheme.add_argument(port_argument)
        user_argument = Argument("username")
        user_argument.title = "Username"
        user_argument.data_type = Argument.data_type_string
        user_argument.description = "mongodb username"
        user_argument.required_on_create = False
        scheme.add_argument(user_argument)
        pass_argument = Argument("password")
        pass_argument.title = "Password"
        pass_argument.data_type = Argument.data_type_string
        pass_argument.description = "mongodb password"
        pass_argument.required_on_create = False
        scheme.add_argument(pass_argument)
        return scheme

    def validate_input(self, definition):
        try:
            int(definition.parameters["port"])
        except:
            raise ValueError("MongoDB port should be an integer")


    @abstractmethod
    def create_scheme(self):
        """ initialize the ```Scheme```
        :return:
        """

    @abstractmethod
    def stream_events_mongo(self, input_name, input_item, client, ew):
        """The method called to stream events into Splunk. It should do all of its output via
        EventWriter rather than assuming that there is a console attached.

        :param input_name: name of the data input stanza
        :param input_item: input configuration element
        :param ew: An object with methods to write events and log messages to Splunk.
        """

    def stream_events(self, inputs, ew):
        for input_name, input_item in inputs.inputs.iteritems():
            host = input_item["server"]
            port = input_item["port"]
            user = input_item["username"]
            pswd = input_item["password"]

            if not port is None:
                port = int(port)

            if not user is None and not pswd is None:
                mongoURI = "mongodb://{username}:{password}@{host}:{port}".format(
                    username = user, password = pswd,
                    host = host, port = port
                )
                client = pymongo.MongoClient(mongoURI)
                self.stream_events_mongo(input_name, input_item, client, ew)
            else:
                client = pymongo.MongoClient(host, port)
                self.stream_events_mongo(input_name, input_item, client, ew)
