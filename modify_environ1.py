# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 21:54:29 2019

@author: Administrator
"""

import os
import sys
from subprocess import check_call
if sys.hexversion > 0x03000000:
    import winreg
else:
    import _winreg as winreg


class Win32Environment:
    """Utility class to get/set windows environment variable"""

    def __init__(self, scope):
        # assert scope in ('user', 'system')
        self.scope = scope
        if scope == 'user':
            self.root = winreg.HKEY_CURRENT_USER
            self.subkey = 'Environment'
        else:
            self.root = winreg.HKEY_LOCAL_MACHINE
            self.subkey = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'

    def getenv(self, name):
        key = winreg.OpenKey(self.root, self.subkey, 0, winreg.KEY_READ)
        try:
            value, _ = winreg.QueryValueEx(key, name)
        except WindowsError:
            value = ''
        return value

    def setenv(self, name, value):
        # Note: for 'system' scope, you must run this as Administrator
        key = winreg.OpenKey(self.root, self.subkey, 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)
        winreg.CloseKey(key)
        # For some strange reason, calling SendMessage from the current process
        # doesn't propagate environment changes at all.
        # TODO: handle CalledProcessError (for assert)
        check_call(
            '''\"%s" -c "import win32api, win32con;assert win32api.SendMessage(win32con.HWND_BROADCAST, win32con.WM_SETTINGCHANGE,0, 'Environment')"''' %
            sys.executable)

    def get_userenv(self, name):
        # Note: for 'system' scope, you must run this as Administrator
        key = winreg.OpenKey(self.root, self.subkey, 0, winreg.KEY_ALL_ACCESS)
        value, _ = winreg.QueryValueEx(key, name)
        return value


def test_winreg():
    e1 = Win32Environment(scope="system")
    print(e1.getenv('PATH'))
#    e2 = Win32Environment(scope="user")
    # e2.setenv('JAVA_HOME', os.path.expanduser('C:\\jdk1.8.0_91'))
    # e2.setenv('CLASS_PATH', os.path.expanduser('%JAVA_HOME%\\lib;%JAVA_HOME%\\lib\\tools.jar'))
    # e2.setenv('PATH', os.path.expanduser('%JAVA_HOME%\\jre\\bin;%JAVA_HOME%\\bin'))
#    print(e2.get_userenv("OneDrive"))
#
#    cmd = "java version"
#
#    e1 = Win32Environment(scope="user")
    # print e1.get_userenv('JAVA_HOME')


if __name__ == '__main__':
    test_winreg()

    # if filename and os.path.isfile(filename):
    #     execfile(filename)
