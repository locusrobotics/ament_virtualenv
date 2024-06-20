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
# \file      combine_requirements
# \authors   Max Krichenbauer <v-krichenbauer7715@esol.co.jp>
# \copyright Copyright (c) (2019), eSol, All rights reserved.
#
from __future__ import print_function

import argparse
import re
import sys

from typing import List, Dict
from io import TextIOWrapper
from collections import namedtuple
from packaging.requirements import Requirement, InvalidRequirement

try:
    from ament_virtualenv.requirements import VcsRequirement
except ImportError:
    try:
        from requirements import VcsRequirement
    except ImportError:
        from .requirements import VcsRequirement

comment_regex = re.compile(r'\s*#\s.*$', flags=re.MULTILINE)

CombinedRequirement = namedtuple("CombinedRequirement", "requirement source suppressed_set")
SuppressedRequirement = namedtuple("SuppressedRequirement", "requirement source")


def combine_requirements(
    requirements_list: List[TextIOWrapper], output_file: TextIOWrapper
) -> int:
    combined_requirements: Dict[str, Requirement] = {}
    for requirements_file in requirements_list:
        contents = requirements_file.read()

        # Filter out any 'comment' lines
        contents = comment_regex.sub('', contents)

        for requirement_string in contents.splitlines():
            if requirement_string and not requirement_string.isspace():
                # First try to match a SemVer requirement then a VCS requirement.
                try:
                    requirement = Requirement(requirement_string)
                except InvalidRequirement as semver_err:
                    try:
                        requirement = VcsRequirement(requirement_string)
                    except InvalidRequirement as vcs_err:
                        raise RuntimeError(
                            "Could not match requirement {} for VCS ({}) or SemVer ({})".format(
                                requirement_string, str(vcs_err), str(semver_err)))

                if requirement.name not in combined_requirements:
                    combined_requirements[requirement.name] = CombinedRequirement(
                        requirement=requirement,
                        source=requirements_file.name,
                        suppressed_set=set()
                    )
                else:
                    combined_requirements[requirement.name].suppressed_set.add(
                        SuppressedRequirement(requirement=requirement,
                                              source=requirements_file.name))

    for entry in combined_requirements.values():
        output_file.write("{} # from {}\n".format(entry.requirement, entry.source))
        for suppressed in entry.suppressed_set:
            output_file.write(
                "# suppressed {} from {}\n".format(suppressed.requirement, suppressed.source)
            )

    return 0


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--requirements-list',
        type=argparse.FileType('r'),
        nargs='*',
        required=True
    )
    parser.add_argument('--output-file', type=argparse.FileType('w'), required=True)
    args, unknown = parser.parse_known_args()

    return combine_requirements(**vars(args))
#


if __name__ == "__main__":
    sys.exit(main())
