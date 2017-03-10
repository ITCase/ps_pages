#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Base classes for tests
http://www.sontek.net/blog/2011/12/01/writing_tests_for_pyramid_and_sqlalchemy.html
"""
# standard library
import imp
import unittest

# SQLAlchemy
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker

# Pyramid
from pyramid import testing
from pyramid.threadlocal import get_current_registry

# third-party
from webtest import TestApp
from pyramid_pages import CONFIG_MODELS, CONFIG_DBSESSION
from sqlalchemy_mptt import mptt_sessionmaker

imp.load_source(
    'pyramid_pages_example',
    'examples/pages/pyramid_pages_example.py'
)

from pyramid_pages_example import (  # noqa isort:skip
    Base,
    WebPage,
    NewsPage,
    main,
    models
)


settings = {
    'sqlalchemy.url': 'sqlite:///test.sqlite',
    'pyramid_pages.models': models
}


class BaseTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = engine_from_config(settings, prefix='sqlalchemy.')
        cls.DBSession = mptt_sessionmaker(sessionmaker())

    def setUp(self):
        # bind an individual Session to the connection
        self.dbsession = self.DBSession(bind=self.engine)
        self.create_db()

    def tearDown(self):
        # rollback - everything that happened with the
        # Session above (including calls to commit())
        # is rolled back.
        testing.tearDown()
        self.drop_db()
        self.dbsession.close()

    def drop_db(self):
        Base.metadata.drop_all(bind=self.engine)
        self.dbsession.commit()

    def create_db(self):
        Base.metadata.create_all(bind=self.engine)
        self.dbsession.commit()


class UnitTestBase(BaseTestCase):

    def setUp(self):
        self.request = testing.DummyRequest()
        self.config = testing.setUp(request=self.request)
        super(UnitTestBase, self).setUp()
        get_current_registry().settings[CONFIG_MODELS] = models
        get_current_registry().settings[CONFIG_DBSESSION] = self.dbsession


class IntegrationTestBase(BaseTestCase):

    def setUp(self):
        self.app = TestApp(main({}, **settings))
        self.config = testing.setUp()
        super(IntegrationTestBase, self).setUp()
