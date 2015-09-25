'''
Setup file for installing shelllogger
'''
from setuptools import setup

setup(
 name = "shelllogger",
 version = "1.0.1",
 author = "Lorin Hochstein, Prakashkumar Thiagarajan",
 author_email = "lorinh@gmail.com, tprak@seas.upenn.edu",
 url = "https://github.com/lorin/shelllogger",
 packages = ["sl"],
 scripts = ['shelllogger','sl-validate','sl-view'],
 description = "Logs shell commands, similar to Unix script program",
)
