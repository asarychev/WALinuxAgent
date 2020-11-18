# import os  # pylint: disable=W0611
# import re  # pylint: disable=W0611
# import pwd  # pylint: disable=W0611
# import shutil  # pylint: disable=W0611
# import socket  # pylint: disable=W0611
# import array  # pylint: disable=W0611
# import struct  # pylint: disable=W0611
# import fcntl  # pylint: disable=W0611
# import time  # pylint: disable=W0611
# import base64  # pylint: disable=W0611
# import azurelinuxagent.common.conf as conf
import azurelinuxagent.common.logger as logger
# from azurelinuxagent.common.future import ustr, bytebuffer  # pylint: disable=W0611
# from azurelinuxagent.common.exception import OSUtilError, CryptError
# import azurelinuxagent.common.utils.fileutil as fileutil
# import azurelinuxagent.common.utils.shellutil as shellutil
# import azurelinuxagent.common.utils.textutil as textutil  # pylint: disable=W0611
# from azurelinuxagent.common.utils.cryptutil import CryptUtil
from azurelinuxagent.common.osutil.default import DefaultOSUtil

class Shim:
    def __init__(self, name, fun):
        self.name = name
        self.fun = fun

    def __call__(self, *args, **kwargs):
        s = ', '.join([str(v) for v in args] + ["{}={}".format(k,v) for (k,v) in kwargs.items()])
        res = self.fun(*args, **kwargs)
        logger.verbose("G> invoked {}({}): '{}'".format(self.name, s, res))
        return res

class GentooOSUtil(DefaultOSUtil):

    def __getattribute__(self, name):
        t = object.__getattribute__(self, name)
        if callable(t):
            return Shim(name, t)
        else:
            logger.verbose("G> getting attribute '{}': '{}'".format(name, t))
            return t

    def register_agent_service(self):
        return shellutil.run("systemctl unmask {0}".format(self.service_name), chk_err=False)

    def unregister_agent_service(self):
        return shellutil.run("systemctl mask {0}".format(self.service_name), chk_err=False)

    def get_dhcp_pid(self):
        return self._get_dhcp_pid(["pidof", "systemd-networkd"])

    def start_network(self):
        return shellutil.run("systemctl start systemd-networkd", chk_err=False)

    def stop_network(self):
        return shellutil.run("systemctl stop systemd-networkd", chk_err=False)

    def start_dhcp_service(self):
        return self.start_network()

    def stop_dhcp_service(self):
        return self.stop_network()

    def start_agent_service(self):
        return shellutil.run("systemctl start {0}".format(self.service_name), chk_err=False)

    def stop_agent_service(self):
        return shellutil.run("systemctl stop {0}".format(self.service_name), chk_err=False)
