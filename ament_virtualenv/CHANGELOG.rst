^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Changelog for package ament_virtualenv
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

0.3.0 (2025-06-06)
------------------
* Fix typo, workspace -> workspaces (#11)
* Fix building from package directory (#10)
  If building from a directory that doesn't contain "src"
  ament_virtualenv would fail to find any packages in the local
  workspace.
* Fix cmake program wrap (#9)
  * Fix broken ament_install_python function
  The upstream package had copied this from catkin_virtualenv and
  updated it for ament. But the templates were not copied, and some
  of the cmake variables were broken and not correct.
  This patch fixes this by copying the install template, fixing the
  broken variables, and removing the "devel" logic as this doesn't
  apply to ROS2 builds.
  * Revert "Remove catkin_pkg in favor of ament_index_python (#4)"
  This reverts commit 8cbdec10a3b01999e6fabe609f974887ec945d9a.
  * Revert "Fix find_in_workspaces to work with bundle prefix paths (#3)"
  This reverts commit 43a3c4d24324bf275b8fec7d770fcd7325e5bd83.
  * Resolve workspace paths before searching workspaces
  The workspace paths included the project name and this directory may
  not even exist yet. This caused os.walk() to return an empty list.
  Fix this by resolving the paths first to remove any ".." paths and
  in turn remove the project name from the overall workspace path.
  * Fix workspace path checks, and support bundle paths
* Don't wrap modules (#7)
  * Don't wrap modules
  * Add flake8 config
* Fixing regex warning (#8)
* Contributors: Gary Servin, James Prestwood, Tom Moore

0.2.0 (2025-02-04)
------------------
* Rename "install" to "install_venv" (#6)
  This script conflicts with the linux tool "install" which is used
  at least by preflight. Since this script isn't even used by
  anything as far as the build system goes rename it to "install_venv"
* Contributors: James Prestwood

0.1.0 (2024-09-16)
------------------
* Wrap binaries under install/lib/{PACKAGE}, not top level (#5)
  * Utilize distutils to simplify/fix the script wrapping
  The current code was wrapping every binary located under
  install/bin, which contains binaries from packages that may not
  be related to ament_virtualenv at all. This was causing failures
  due to the venv being used when it shouldn't.
  Instead of having each package define its own install class and
  call venv_install, create an AmentVirtualenvInstall class that
  can be imported and used by packages. All the information we need
  is stored by distutils so there is no need for the package to
  define it. This install class will also parse the entry_points and
  only wrap scripts defined there, thereby isolating the venv only
  to scripts installed by the package.
  Extra options are now possible, similar to catkin_virtualenv by
  defining an "ament_virtualenv" dictionary within the options
  argument to setup().
  setup(
  # ...
  options={
  "ament_virtualenv": {
  "use_system_packages": True,
  "python_version": "3.10"
  }
  }
  }
  * Add typing for arguments/return values
  This should be done going forward as changes are made to improve
  code readability.
* Remove catkin_pkg in favor of ament_index_python (#4)
  The fix using catkin_pkg was actually not working as expected. It
  will only search ROS1 paths which means that pure-ROS2 packages
  were broken. This got missed because all the testing was done with
  locus_py, which did exist as a ROS1 package.
* Fix find_in_workspaces to work with bundle prefix paths (#3)
  * Fix find_in_workspaces to work with bundle prefix paths
  The logic in here required that "/install/" be part of the prefix
  path. This is not the case for our bundle which just points to the
  root directory.
  Instead just copy what catkin_virtualenv does and use catkin_pkg's
  own find_in_workspaces API.
  * Fix build warning due to no marker in package
* Package wide linting fixes (#2)
* Fix a few issues with the upstream project:
  - After upgrading pip "python -m pip" fails. This was fixed
  by setting the pip version to None
  - Update package.xml to use python3-venv
  - Update hard coded python2 versions to python3
  - Fix issue where the <package>/bin directory is missing. Check
  if it exists before calling listdir()
  - Fix tests to work
  Some of the updates were taken from this fork:
  https://github.com/LCAS/ament_virtualenv
* Contributors: James Prestwood

0.0.5 (2020-01-10)
------------------
* fixed various bugs identified by CI

0.0.4 (2019-12-09)
------------------
* added fallbacks for different environments

0.0.3 (2019-12-04)
------------------
* various bug-fixes

0.0.2 (2019-11-21)
------------------
* various bug-fixes

0.0.1 (2019-10-21)
------------------
* first public release
