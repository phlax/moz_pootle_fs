# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
#
# This file is a part of the Pootle project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from lxml import etree

from translate.storage.namespace import NS_XLIFF_1_2, XSD_XLIFF_1_2, NS_XSI

from pootle_store.serializers import Deserializer

from .serializers import XMLPrettySerializer


XML_IOS = (
    '<xliff xmlns="%s" xmlns:xsi="%s" version="%s" xsi:schemaLocation="%s %s">'
    '</xliff>')

IOS_TOOL_HEADER = (
    ("tool-id", "com.apple.dt.xcode"),
    ("tool-name", "Xcode"),
    ("tool-version", "7.3"),
    ("build-num", "7D175"))


class IOSSerializer(XMLPrettySerializer):

    @property
    def xliff_root_node(self):
        return etree.fromstring(
            XML_IOS
            % (NS_XLIFF_1_2,
               NS_XSI,
               1.2,
               NS_XLIFF_1_2,
               XSD_XLIFF_1_2),
            parser=self.parser)

    def create_tool_header(self):
        tool = etree.Element("tool")
        for k, v in IOS_TOOL_HEADER:
            tool.set(k, v)
        return tool

    def create_file_header(self):
        header = etree.Element("header")
        header.insert(0, self.create_tool_header())
        return header

    def get_body_element(self, xml, filename,
                         source_language, target_language):
        existing = xml.xpath(
            "./file["
            "@original='%s' "
            "and @source-language='%s' "
            "and @target-language='%s']"
            % (filename,
               source_language,
               target_language))
        if existing:
            return existing[0].xpath("./body")[0]
        fileel = etree.Element("file")
        fileel.set("original", filename)
        fileel.set("source-language", source_language)
        fileel.set("datatype", "plaintext")
        fileel.set("target-language", target_language)
        xml.append(fileel)
        body = etree.Element("body")
        fileel.append(self.create_file_header())
        fileel.append(body)
        return body

    def create_file_element(self, node, filename):
        current_filenode = node.getparent().getparent()
        source_language = current_filenode.get("source-language")
        target_language = current_filenode.get("target-language")
        self.get_body_element(
            node.getroottree().getroot(),
            filename,
            source_language,
            target_language).insert(2, node)

    def handle_unit_node(self, node):
        original_id = node.get("id")
        filename = node.get("id").split("__%04__")[0]
        node.set("id", original_id.split("__%04__").pop())
        for k in [i for i in node.keys() if i != "id"]:
            etree.strip_attributes(node, k)
        self.create_file_element(node, filename)

    def reorder_units(self, xml):
        unit_nodes = xml.xpath('//trans-unit')
        for node in unit_nodes:
            self.handle_unit_node(node)
        return xml

    def serialize(self, xml):
        xml = self.convert_doc(xml, self.xliff_root_node)
        xml = self.remove_empty(xml, '//target')
        xml = self.reorder_units(xml)
        xml = self.remove_empty(xml, '//body')
        xml = self.remove_empty(xml, '//file')
        return super(IOSSerializer, self).serialize(xml)


class IOSDeserializer(Deserializer):

    @property
    def output(self):
        return self.data
