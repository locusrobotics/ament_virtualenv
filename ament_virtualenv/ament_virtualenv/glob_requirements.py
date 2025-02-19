#!/usr/bin/env python
#
# Copyright 2019 eSOL Co.,Ltd.
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
# \file      glob_requirements
# \authors   Max Krichenbauer <v-krichenbauer7715@esol.co.jp>
# \copyright Copyright (c) (2019), eSol, All rights reserved.
#
from __future__ import print_function

import argparse
import sys

from typing import List
from catkin_pkg.package import Package
from catkin.find_in_workspaces import find_in_workspaces

try:
    from ament_virtualenv.package import parse_package
except ImportError:
    try:
        from package import parse_package
    except ImportError:
        from .package import parse_package

try:
    from queue import Queue
except ImportError:
    from Queue import Queue


AMENT_VIRTUALENV_TAGNAME = "pip_requirements"


def parse_exported_requirements(package: Package) -> List[str]:
    requirements_list = []
    for export in package.exports:
        if export.tagname == AMENT_VIRTUALENV_TAGNAME:
            requirements_path = find_in_workspaces(
                project=package.name,
                path=export.content,
                first_match_only=True
            )[0]
            if not requirements_path:
                print(
                    ("[ERROR] ament_virtualenv "
                     "Package {package} declares <{tagname}> {file}, "
                     "which cannot be found in the package").format(
                        package=package.name,
                        tagname=AMENT_VIRTUALENV_TAGNAME,
                        file=export.content
                    ),
                    file=sys.stderr
                )
            else:
                requirements_list.append(requirements_path)
    return requirements_list


def process_package(package_name, soft_fail=True):
    # type: (str) -> List[str], List[str]
    try:
        package_path = find_in_workspaces(
            project=package_name, path="package.xml", first_match_only=True,
        )[0]
    except IndexError:
        if not soft_fail:
            raise RuntimeError("Unable to process package {}".format(package_name))
        else:
            # This is not an ament dependency
            return [], []
    else:
        package = parse_package(package_path)
        dependencies = package.build_depends + package.test_depends
        return parse_exported_requirements(package), dependencies


def glob_requirements(package_name, no_deps):
    # type: (str) -> int
    package_queue = Queue()
    package_queue.put(package_name)
    processed_packages = set()
    requirements_list = []

    while not package_queue.empty():
        queued_package = package_queue.get()

        if queued_package not in processed_packages:
            processed_packages.add(queued_package)
            requirements, dependencies = process_package(
                package_name=queued_package, soft_fail=(queued_package != package_name))
            requirements_list = requirements_list + requirements

            if not no_deps:
                for dependency in dependencies:
                    package_queue.put(dependency.name)
    return ';'.join(requirements_list)


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-name', type=str, required=True)
    parser.add_argument('--no-deps', action="store_true")
    args, unknown = parser.parse_known_args()
    print(glob_requirements(**vars(args)))
    return 0
#


if __name__ == "__main__":
    sys.exit(main())
