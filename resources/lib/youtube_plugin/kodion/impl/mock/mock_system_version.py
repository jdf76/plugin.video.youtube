__author__ = 'bromix'

from ..abstract_system_version import AbstractSystemVersion


class MockSystemVersion(AbstractSystemVersion):
    def __init__(self, major, minor, releasename, appname):
        AbstractSystemVersion.__init__(self, (major, minor), releasename, appname)
