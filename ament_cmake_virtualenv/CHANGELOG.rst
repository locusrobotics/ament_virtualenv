^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Changelog for package ament_cmake_virtualenv
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

0.3.0 (2025-06-06)
------------------
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
* Contributors: Gary Servin, James Prestwood

0.2.0 (2025-02-04)
------------------

0.1.0 (2024-09-16)
------------------
* Package wide linting fixes (#2)
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
