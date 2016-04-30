# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
#
# This file is a part of the Pootle project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import re

from lxml import etree, objectify

from django.utils.functional import cached_property

from pootle_store.serializers import Serializer


class NoEmptyLineSerializer(Serializer):

    @property
    def output(self):
        return u"\n".join(
            filter(
                lambda x: not re.match(r'^\s*$', x),
                self.data.split("\n")))


class XMLSerializer(Serializer):

    parser = None

    @property
    def data(self):
        return self.original_data.encode("utf8")

    @property
    def output(self):
        return self.serialize(self.xml).decode("utf8")

    def serialize(self, xml):
        return etree.tostring(xml)

    @cached_property
    def xml(self):
        return etree.fromstring(
            self.data,
            parser=self.parser)

    def convert_doc(self, xml, root_node):
        """Converts to an XML doc to new namespace
        and scrubs old element ns
        """
        for elem in xml.getiterator():
            if not hasattr(elem.tag, 'find'):
                continue
            i = elem.tag.find('}')
            if i >= 0:
                elem.tag = elem.tag[i+1:]
        objectify.deannotate(xml, cleanup_namespaces=True)
        root_node[:] = xml[:]
        return root_node

    def remove_empty(self, xml, path):
        for node in xml.xpath(path):
            if not node.text and not node.getchildren():
                parent = node.getparent()
                if node.getnext() is None and node.getprevious() is not None:
                    previous = node.getprevious()
                    previous.tail = previous.tail[:-2]
                parent.remove(node)
        return xml

    def strip_attributes(self, xml, path, attrs):
        for node in xml.xpath(path):
            for k in [i for i in node.keys() if i in attrs]:
                etree.strip_attributes(node, k)
        return xml


class XMLPrettySerializer(XMLSerializer):

    @property
    def parser(self):
        return etree.XMLParser(remove_blank_text=True)

    def serialize(self, xml):
        return etree.tostring(
            xml,
            xml_declaration=True,
            encoding="UTF-8",
            pretty_print=True)
