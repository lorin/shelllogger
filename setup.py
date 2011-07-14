'''
Setup file for installing shelllogger
'''

from setuptools import setup

setup(
 name = "ShellLogger",
 version = "1.0",
 author = "Lorin Hochstein, Prakashkumar Thiagarajan",
 author_email = "lorinh@gmail.com, tprak@seas.upenn.edu",
 url = "http://code.google.com/p/shelllogger/",
 requires = ['pkg_resources'],
 packages = ['source'],
 description = "Logs shell commands, similar to Unix script program",
 scripts = ['shelllogger','sl-view','sl-validate']
)
