# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
#
# This file is a part of the Pootle project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from pootle.core.plugin import provider

from pootle.core.delegate import serializers, deserializers

from .ios import IOSSerializer, IOSDeserializer


@provider(serializers)
def moz_serializer_providers(**kwargs):
    return dict(ios=IOSSerializer)


@provider(deserializers)
def moz_deserializer_providers(**kwargs):
    return dict(ios=IOSDeserializer)
