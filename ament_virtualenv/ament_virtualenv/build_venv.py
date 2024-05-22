#!/usr/bin/env python
#
# Copyright 2019 eSol Co.,Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#
# \file      build_venv
# \authors   Max Krichenbauer <v-krichenbauer7715@esol.co.jp>
# \copyright Copyright (c) (2019), eSol Co.,Ltd., All rights reserved.
#
from __future__ import print_function

import argparse
import os
import re
import shutil
import subprocess
import sys

from ament_virtualenv.deployment import Deployment
from distutils.spawn import find_executable


_BYTECODE_REGEX = re.compile('.*.py[co]')


def delete_bytecode(directory):
    for root, _, files in os.walk(directory):
        for f in files:
            if _BYTECODE_REGEX.match(f):
                os.remove(os.path.join(root, f))


def find_python(version):
    python_executable = find_executable('python' + version)
    if not python_executable:
        raise RuntimeError("Unable to find python executable 'python{}''".format(version))
    return python_executable


def check_module(python_executable, module):
    try:
        with open(os.devnull, 'w') as devnull:
            # "-c 'import venv'" does not work with the subprocess module, but '-cimport venv' does
            subprocess.check_call(
                [python_executable, '-cimport {}'.format(module)],
                stderr=devnull
            )
        return True
    except subprocess.CalledProcessError:
        return False


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description=(
            "Build a virtualenv, and rewrite the internal paths with an arbitrary root directory."
        )
    )
    parser.add_argument(
        '--requirements',
        required=True,
        help="A requirements.txt file specifying dependencies."
    )
    parser.add_argument(
        '--root-dir',
        required=True,
        help="Directory to which the virtualenv's hardcoded paths should be rewritten."
    )
    parser.add_argument(
        '--python-version',
        required=True,
        help="Build the virtualenv with which python major version."
    )
    parser.add_argument(
        '--retries',
        type=int,
        default=0,
        help="Number of times to retry buiding virtualenv."
    )
    parser.add_argument(
        '--use-system-packages',
        action="store_true",
        help="Use system site packages."
    )
    parser.add_argument(
        '--extra-pip-args',
        default="\"\"",
        type=str,
        help="Extra pip args for install."
    )
    args, unknown = parser.parse_known_args()
    return build_venv(
        root_dir=args.root_dir,
        python_version=args.python_version,
        requirements_filename=args.requirements,
        use_system_packages=args.use_system_packages,
        extra_pip_args=args.extra_pip_args[1:-1],
        retries=args.retries
    )


def build_venv(root_dir,
               python_version,
               requirements_filename,
               use_system_packages=False,
               extra_pip_args="",
               retries=0):
    root_dir = os.path.realpath(root_dir)
    python_executable = find_python(python_version)
    os.environ['DH_VIRTUALENV_INSTALL_ROOT'] = os.path.dirname(root_dir)

    deploy = Deployment(
        package=os.path.basename(root_dir),
        requirements_filename=requirements_filename,
        upgrade_pip=False,
        use_system_packages=use_system_packages,
        python=python_executable,
        extra_pip_arg=extra_pip_args.split(' '),
        log_file=None,
        builtin_venv=check_module(python_executable, 'venv'),
        builtin_pip=check_module(python_executable, 'pip'),
        pip_version=None  # (pbovbel) known working version
    )

    while True:
        try:
            print('Generating virtualenv in {}'.format(deploy.package_dir))
            deploy.create_virtualenv()

            print('Installing requirements from {}'.format(deploy.requirements_filename))
            deploy.install_dependencies()

            print('Fixing virtualenv root to {}'.format(deploy.virtualenv_install_dir))
            deploy.fix_activate_path()
            deploy.fix_shebangs()
            deploy.fix_local_symlinks()

            # Remove all .py[co] files since they embed absolute paths
            delete_bytecode(deploy.package_dir)

            local_dir = os.path.join(deploy.package_dir, 'local')
            if os.path.exists(local_dir):
                # Remove local folder
                shutil.rmtree(local_dir)
        except Exception as e:
            retries -= 1
            if retries >= 0:
                print("Error, clearing virtualenv and retrying: {}".format(e), file=sys.stderr)
                try:
                    shutil.rmtree(root_dir)
                except OSError:
                    pass
                continue
            else:
                raise
        break

    return 0
#


if __name__ == "__main__":
    sys.exit(main())
