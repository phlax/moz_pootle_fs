# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
#
# This file is a part of the Pootle project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import pytest

from pootle.core.delegate import serializers, deserializers
from pootle_store.models import Store

from moz_pootle_fs.serializers import NoEmptyLineSerializer
from moz_pootle_fs.ios import IOSSerializer, IOSDeserializer


@pytest.mark.django_db
def test_moz_ios():
    ios_serializers = serializers.gather(Store)
    assert "ios" in ios_serializers
    assert ios_serializers["ios"] is IOSSerializer

    ios_deserializers = deserializers.gather(Store)
    assert "ios" in ios_deserializers
    assert ios_deserializers["ios"] is IOSDeserializer


@pytest.mark.django_db
def test_moz_ios_deserializer(ios_store, ios_file):
    data = IOSDeserializer(ios_store, ios_file).output
    assert data == ios_file


@pytest.mark.django_db
def test_moz_ios_serializers(ios_store, ios_file):

    data = ios_store.serialize()

    ios_serializers = [NoEmptyLineSerializer, IOSSerializer]

    for serializer in ios_serializers:
        data = serializer(ios_store, data).output

    assert data.strip() == ios_file.strip()


@pytest.mark.django_db
def test_moz_ios_project_serializers(ios_store, ios_file):
    
    project = ios_store.translation_project.project
    project.serializers = "ios"
    project.save()

    data = ios_store.serialize()

    assert data.strip() == ios_file.strip()

