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
import os

from pathlib import Path
from typing import List
from catkin_pkg.package import Package
from ament_index_python.packages import get_package_share_directory, PackageNotFoundError

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


def find_in_workspaces(project, file, workspaces=[]):
    # A source directory should be passed within 'workspaces' (i.e. a local workspace),
    # but if not try and get the package path from ament. This will handle packages
    # that aren't in the local workspace.
    try:
        path = get_package_share_directory(project)
        workspaces.append(path)
    except PackageNotFoundError:
        pass

    if len(workspaces) == 0:
        raise RuntimeError(
            "[ament_virtualenv] Failed to find any workspaces." +
            "\nAMENT_PREFIX_PATH=" + os.environ.get('AMENT_PREFIX_PATH', 'NOT SET') +
            "\nCMAKE_PREFIX_PATH=" + os.environ.get('CMAKE_PREFIX_PATH', 'NOT SET') +
            "\nCOLCON_PREFIX_PATH=" + os.environ.get('COLCON_PREFIX_PATH', 'NOT SET') +
            "\nCWD=" + os.getcwd()
        )

    # The paths in "workspaces" will look something like (depending on logic above)
    # <prefix>/install/<project>/../
    # The issue here is <project> dir may not actually exist so below when we walk the
    # directories it will ignore that folder since it doesn't exist. To fix this we
    # need to resolve the paths so they point to valid directories, ignoring the dir
    # of the packages we're building which may not exist.
    workspaces = [str(Path(path).resolve()) for path in workspaces]

    for workspace in (workspaces or []):
        # Shortcut so we don't have to search the entire install tree
        if os.path.exists(f"{workspace}/{project}/share/{project}/{file}"):
            return f"{workspace}/{project}/share/{project}/{file}"

    # Now search the workspaces. Since this may point to the distro root which
    # will contain ignore files we need to ignore that directory i.e. d != workspace.
    for workspace in (workspaces or []):
        for d, dirs, files in os.walk(workspace, topdown=True, followlinks=True):
            if (('CATKIN_IGNORE' in files) or
               ('COLCON_IGNORE' in files) or
               ('AMENT_IGNORE' in files)) and d != workspace:
                del dirs[:]
                continue
            dirname = os.path.basename(d)
            if dirname == project and file in files:
                return os.path.join(workspace, d, file)
    # none found:
    return None
#


AMENT_VIRTUALENV_TAGNAME = "pip_requirements"


def parse_exported_requirements(package: Package, source_dir: str) -> List[str]:
    requirements_list = []
    for export in package.exports:
        if export.tagname == AMENT_VIRTUALENV_TAGNAME:
            requirements_path = find_in_workspaces(
                project=package.name,
                file=export.content,
                workspaces=[source_dir]
            )
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


def process_package(package_name, source_dir=None, soft_fail=True):
    # type: (str) -> List[str], List[str]
    workspaces = []
    if source_dir:
        workspaces.append(source_dir)

    package_path = find_in_workspaces(
        project=package_name,
        file="package.xml",
        workspaces=workspaces
    )
    if not package_path:
        if not soft_fail:
            raise RuntimeError("Failed to find package.xml for package " +
                               package_name + ' in ' + ';'.join(workspaces))
        else:
            # This is not an ament dependency
            return [], []
    else:
        package = parse_package(package_path)
        dependencies = package.build_depends + package.test_depends
        return parse_exported_requirements(package, source_dir), dependencies


def glob_requirements(package_name, source_dir, no_deps):
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
                package_name=queued_package, source_dir=source_dir, soft_fail=(queued_package != package_name))
            requirements_list = requirements_list + requirements

            if not no_deps:
                for dependency in dependencies:
                    package_queue.put(dependency.name)
    return ';'.join(requirements_list)


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-name', type=str, required=True)
    parser.add_argument('--source-dir', type=str)
    parser.add_argument('--no-deps', action="store_true")
    args, unknown = parser.parse_known_args()
    print(glob_requirements(**vars(args)))
    return 0
#


if __name__ == "__main__":
    sys.exit(main())
