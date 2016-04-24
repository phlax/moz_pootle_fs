# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
#
# This file is a part of the Pootle project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import pytest


@pytest.fixture
def ios_project():
    from pootle_project.models import Project

    return Project.objects.get(code="ios")


@pytest.fixture
def ios_tp(ios_project):
    return ios_project.translationproject_set.get(
        language__code="language0")


@pytest.fixture
def ios_store(ios_tp):
    return ios_tp.stores.get(name="firefox-ios.xliff")
