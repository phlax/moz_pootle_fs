# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
#
# This file is a part of the Pootle project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

import io
import os
import tempfile

from git import Repo

import pytest

from translate.storage.factory import getclass

from pootle_fs_git.utils import tmp_git


@pytest.fixture(scope="session")
def ios_file():
    ios_xliff = os.path.join(
        os.path.dirname(__file__),
        "data/firefox-ios.xliff")
    with open(ios_xliff) as xliff_file:
        content = xliff_file.read().decode("utf8")
    return content


@pytest.fixture(scope="session")
def ios_pootle_file():
    ios_xliff = os.path.join(
        os.path.dirname(__file__),
        "data/pootle-firefox-ios.xliff")
    with open(ios_xliff) as xliff_file:
        content = xliff_file.read().decode("utf8")
    return content


@pytest.fixture(scope="session", autouse=True)
def moz_env(post_db_setup, _django_cursor_wrapper, ios_pootle_file):

    from django.conf import settings

    from pytest_pootle.factories import (
        ProjectDBFactory, StoreDBFactory,
        TranslationProjectFactory)

    from pootle_fs.models import ProjectFS
    from pootle_language.models import Language

    with _django_cursor_wrapper:
        ios_project = ProjectDBFactory(
            source_language=Language.objects.get(code="en"),
            code="ios",
            localfiletype="xliff")
        ios_tp = TranslationProjectFactory(
            project=ios_project,
            language=Language.objects.get(code="language0"))
        ios_store = StoreDBFactory(
            parent=ios_tp.directory,
            translation_project=ios_tp,
            name="firefox-ios.xliff")
        ios_bytes = io.BytesIO(ios_pootle_file.encode("utf8"))
        ios_store.update(
            getclass(ios_bytes)(ios_bytes.read()))

        fs_dir = tempfile.mkdtemp()
        settings.POOTLE_FS_PATH = fs_dir

        repo_path = os.path.join(fs_dir, "__moz_ios_src__")
        Repo.init(repo_path, bare=True)

        with tmp_git(repo_path) as (tmp_repo_path, tmp_repo):
            config_file = os.path.join(tmp_repo_path, ".pootle.ini")
            with open(config_file, "w") as ini:
                config = (
                    "[default]\n"
                    "serializers = ios\n"
                    "deserializers = ios\n"
                    "translation_path = <lang>/<filename>.xliff")
                ini.write(config)
            tmp_repo.index.add([".pootle.ini"])
            tmp_repo.index.commit("Add Pootle configuration")
            tmp_repo.remotes.origin.push("master:master")

        ios_fs = ProjectFS.objects.create(
            project=ios_project,
            fs_type="git",
            url=repo_path)
        ios_plugin = ios_fs.plugin
        ios_plugin.add_translations()
