#!/usr/bin/env python

import argparse
import os
import subprocess
import sys

from lib.config import LIBCHROMIUMCONTENT_COMMIT, BASE_URL
from lib.util import execute, scoped_cwd


SOURCE_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
VENDOR_DIR = os.path.join(SOURCE_ROOT, 'vendor')
PYTHON_26_URL = 'https://chromium.googlesource.com/chromium/deps/python_26'
NPM = 'npm.cmd' if sys.platform == 'win32' else 'npm'


def main():
  os.chdir(SOURCE_ROOT)

  args = parse_args()
  update_submodules()
  update_npm()
  update_node_modules('.')
  update_atom_modules('atom/browser/default_app')
  bootstrap_brightray(args.url)
  if sys.platform == 'cygwin':
    update_win32_python()

  touch_config_gypi()
  update_atom_shell()


def parse_args():
  parser = argparse.ArgumentParser(description='Bootstrap this project')
  parser.add_argument('-u', '--url',
                      help='The base URL from which to download '
                      'libchromiumcontent (i.e., the URL you passed to '
                      'libchromiumcontent\'s script/upload script',
                      default=BASE_URL,
                      required=False)
  return parser.parse_args()


def update_submodules():
  execute(['git', 'submodule', 'sync'])
  execute(['git', 'submodule', 'update', '--init', '--recursive'])


def bootstrap_brightray(url):
  bootstrap = os.path.join(VENDOR_DIR, 'brightray', 'script', 'bootstrap')
  execute([sys.executable, bootstrap, '--commit', LIBCHROMIUMCONTENT_COMMIT,
           url])


def update_npm():
  global NPM
  if os.environ.get('CI') == '1':
    execute([NPM, 'install', 'npm'])
    NPM = os.path.join(SOURCE_ROOT, 'node_modules', '.bin', 'npm')
    if sys.platform == 'win32':
      NPM += '.cmd'

def update_node_modules(dirname):
  with scoped_cwd(dirname):
    execute([NPM, 'install'])


def update_atom_modules(dirname):
  with scoped_cwd(dirname):
    apm = os.path.join(SOURCE_ROOT, 'node_modules', '.bin', 'apm')
    if sys.platform in ['win32', 'cygwin']:
      apm += '.cmd'
    execute([apm, 'install'])


def update_win32_python():
  with scoped_cwd(VENDOR_DIR):
    if not os.path.exists('python_26'):
      execute(['git', 'clone', PYTHON_26_URL])


def touch_config_gypi():
  config_gypi = os.path.join(SOURCE_ROOT, 'vendor', 'node', 'config.gypi')
  with open(config_gypi, 'w+') as f:
    content = '\n{}'
    if f.read() != content:
      f.write(content)


def update_atom_shell():
  update = os.path.join(SOURCE_ROOT, 'script', 'update.py')
  execute([sys.executable, update])


if __name__ == '__main__':
  sys.exit(main())
