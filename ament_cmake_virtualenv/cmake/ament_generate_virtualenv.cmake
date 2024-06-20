# Copyright 2019-2020 eSOL Co.,Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

function(ament_generate_virtualenv)
  set(oneValueArgs PYTHON_VERSION PYTHON_VERSION_MAJOR USE_SYSTEM_PACKAGES ISOLATE_REQUIREMENTS)
  set(multiValueArgs EXTRA_PIP_ARGS)
  cmake_parse_arguments(ARG "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

  # Check if this package already has a virtualenv target before creating one
  if(TARGET ${PROJECT_NAME}_generate_virtualenv)
    message(WARNING "ament_generate_virtualenv was called twice")
    return()
  endif()

  # Backwards compatibility for PYTHON_VERSION_MAJOR, overriding PYTHON_VERSION
  if(DEFINED ARG_PYTHON_VERSION_MAJOR)
    set(ARG_PYTHON_VERSION ${ARG_PYTHON_VERSION_MAJOR})
    message(WARNING "PYTHON_VERSION_MAJOR has been deprecated, please set PYTHON_VERSION instead")
  endif()

  if(NOT DEFINED ARG_PYTHON_VERSION)
    set(ARG_PYTHON_VERSION 3)
  endif()

  if(NOT DEFINED ARG_USE_SYSTEM_PACKAGES)
    set(ARG_USE_SYSTEM_PACKAGES TRUE)
  endif()

  if(NOT DEFINED ARG_ISOLATE_REQUIREMENTS)
    set(ARG_ISOLATE_REQUIREMENTS FALSE)
  endif()

  if(NOT DEFINED ARG_EXTRA_PIP_ARGS)
    set(ARG_EXTRA_PIP_ARGS "-qq")
  endif()
  # Convert CMake list to ' '-separated list
  string(REPLACE ";" "\ " processed_pip_args "${ARG_EXTRA_PIP_ARGS}")
  # Double-escape needed to get quote down through cmake->make->shell layering
  set(processed_pip_args \\\"${processed_pip_args}\\\")

  set(venv_dir "venv")

  set(venv_install_dir ${CMAKE_INSTALL_PREFIX}/share/${PROJECT_NAME}/${venv_dir})

  set(${PROJECT_NAME}_VENV_INSTALL_DIR ${venv_install_dir} PARENT_SCOPE)

  if(${ARG_ISOLATE_REQUIREMENTS})
    message(STATUS "Only using requirements from this ament package")
    set(glob_args "--no-deps")
  endif()

  # Collect all exported pip requirements files, from this package and all dependencies
  find_program(glob_requirements_BIN NAMES "glob_requirements"
    PATHS "${CMAKE_INSTALL_PREFIX}/../ament_virtualenv/bin/")
  if(NOT glob_requirements_BIN)
    message(FATAL_ERROR "could not find program 'glob_requirements'")
  endif()
  execute_process(
    COMMAND ${glob_requirements_BIN}
      --package-name ${PROJECT_NAME} ${glob_args}
    OUTPUT_VARIABLE requirements_list
    OUTPUT_STRIP_TRAILING_WHITESPACE
  )

  # Include common requirements that ROS makes available in system environment for py2
  list(APPEND requirements_list ${ament_cmake_virtualenv_DIR}/common_requirements.txt)
  set(generated_requirements ${CMAKE_BINARY_DIR}/generated_requirements.txt)
  # Trigger a re-configure if any requirements file changes
  foreach(requirements_txt ${requirements_list})
    stamp(${requirements_txt})
    message(STATUS "Including ${requirements_txt} in bundled virtualenv")
  endforeach()

  # Combine requirements into one list
  find_program(combine_requirements_BIN NAMES "combine_requirements"
    PATHS "${CMAKE_INSTALL_PREFIX}/../ament_virtualenv/bin/")
  if(NOT combine_requirements_BIN)
    message(FATAL_ERROR "could not find program 'combine_requirements'")
  endif()
  add_custom_command(OUTPUT ${generated_requirements}
    COMMAND ${combine_requirements_BIN}
      --requirements-list ${requirements_list} --output-file ${generated_requirements}
    DEPENDS ${requirements_list}
  )

  if(${ARG_USE_SYSTEM_PACKAGES})
    message(STATUS "Using system site packages")
    set(venv_args "--use-system-packages")
  endif()

  # Generate a virtualenv, fixing up paths for install-space
  find_program(build_venv_BIN NAMES "build_venv"
    PATHS "${CMAKE_INSTALL_PREFIX}/../ament_virtualenv/bin/")
  if(NOT build_venv_BIN)
    message(FATAL_ERROR "could not find program 'build_venv'")
  endif()
  add_custom_command(OUTPUT ${venv_install_dir}
    COMMAND ${build_venv_BIN}
      --root-dir ${venv_install_dir} --requirements ${generated_requirements} --retries 3
      --python-version ${ARG_PYTHON_VERSION} ${venv_args} --extra-pip-args ${processed_pip_args}
    DEPENDS ${generated_requirements}
  )

  # Per-package virtualenv target
  add_custom_target(${PROJECT_NAME}_generate_virtualenv ALL
    DEPENDS ${venv_install_dir}
    SOURCES ${requirements_list}
  )

  install(DIRECTORY ${venv_install_dir}
    DESTINATION ${CMAKE_INSTALL_PREFIX}/share/${PROJECT_NAME}
    USE_SOURCE_PERMISSIONS
  )

  install(FILES ${generated_requirements}
    DESTINATION share/${PROJECT_NAME}
  )


  # Override the ament_python_install_module macro to wrap modules
  find_program(wrap_module_BIN NAMES "wrap_module"
    PATHS "${CMAKE_INSTALL_PREFIX}/../ament_virtualenv/bin/")
  if(NOT wrap_module_BIN)
    message(FATAL_ERROR "could not find program 'wrap_module'")
  endif()
  macro(ament_python_install_module)
    _ament_cmake_python_register_environment_hook()
    _ament_cmake_python_install_module(${ARGN})
    get_filename_component(module_path ${ARGN} NAME)
    set(module_path "${CMAKE_INSTALL_PREFIX}/${PYTHON_INSTALL_DIR}/${module_path}")
    # message(
    #   WARNING "[ament_cmake_virtualenv]: ament_python_install_module override for ${module_path} to ${${PROJECT_NAME}_VENV_INSTALL_DIR}"
    # )
    install(
      CODE "execute_process(\
COMMAND ${wrap_module_BIN} --module-path ${module_path} --venv-install-dir ${${PROJECT_NAME}_VENV_INSTALL_DIR})"
    )
  endmacro()

  # Override the ament_python_install_package macro to wrap packages
  find_program(wrap_package_BIN NAMES "wrap_package"
    PATHS "${CMAKE_INSTALL_PREFIX}/../ament_virtualenv/bin/")
  if(NOT wrap_package_BIN)
    message(FATAL_ERROR "could not find program 'wrap_package'")
  endif()
  macro(ament_python_install_package)
    _ament_cmake_python_register_environment_hook()
    _ament_cmake_python_install_package(${ARGN})
    set(package_dir "${CMAKE_INSTALL_PREFIX}/${PYTHON_INSTALL_DIR}/${ARGN}")
    # message(
    #   WARNING "[ament_cmake_virtualenv]: ament_python_install_package override for ${package_dir} to ${${PROJECT_NAME}_VENV_INSTALL_DIR}"
    # )
    install(
      CODE "execute_process(\
COMMAND ${wrap_package_BIN} --package-dir ${package_dir} --venv-install-dir ${${PROJECT_NAME}_VENV_INSTALL_DIR})"
    )
  endmacro()
endfunction()
