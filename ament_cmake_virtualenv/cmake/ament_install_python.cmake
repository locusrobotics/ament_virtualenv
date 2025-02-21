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

function(ament_install_python)
  # See https://github.com/ros/ament/blob/kinetic-devel/cmake/ament_install_python.cmake for overriden function
  cmake_parse_arguments(ARG "OPTIONAL" "DESTINATION" "PROGRAMS" ${ARGN})
  if(NOT ARG_PROGRAMS)
    message(FATAL_ERROR "ament_install_python() called without required PROGRAMS argument.")
  endif()
  if(NOT ARG_DESTINATION)
    message(FATAL_ERROR "ament_install_python() called without required DESTINATION argument.")
  endif()

  if(NOT TARGET ${PROJECT_NAME}_generate_virtualenv)
    message(FATAL_ERROR "${PROJECT_NAME} loaded ament_virtualenv, but never invoked 'ament_generate_virtualenv'")
    return()
  endif()

  # Use CMake templating to create virtualenv loaders for all specified python scripts
  set(install_programs "")

  foreach(program_path ${ARG_PROGRAMS})
    if(NOT IS_ABSOLUTE ${program_path})
      set(program_path "${CMAKE_CURRENT_SOURCE_DIR}/${program_path}")
    endif()
    get_filename_component(program_basename ${program_path} NAME)

    if(EXISTS ${program_path})
      stamp(${program_path})  # Reconfigure when the python script changes. This mirrors upstream behaviour.

      execute_process(
        COMMAND ${AMENT_ENV} test -x ${program_path}
        RESULT_VARIABLE is_program_executable
      )

      if(is_program_executable STREQUAL "0")
        message(WARNING "Making ${program_path} non-executable. Otherwise 'rosrun ${PROJECT_NAME} ${program_basename}' \
will not work as expected.")
        execute_process(
          COMMAND ${AMENT_ENV} chmod -x ${program_path}  # This is touching the source space
        )
      endif()

      set(program_install_location ament_virtualenv_scripts)

      # For install-space support, we install the source script, and then generate a bash script to invoke it using
      # the virtualenv's python interpreter.
      set(install_program ${CMAKE_BINARY_DIR}/${program_basename})
      configure_file(${ament_cmake_virtualenv_DIR}/templates/program.install.in ${install_program})
      execute_process(
        COMMAND ${AMENT_ENV} chmod +x ${install_program}
      )

      install(
        FILES ${program_path}
        DESTINATION ${program_install_location}
      )

      install(
        PROGRAMS ${install_program}
        DESTINATION ${ARG_DESTINATION}
      )

    elseif(NOT ARG_OPTIONAL)
      message(FATAL_ERROR "ament_install_python() called with non-existent file '${program_path}'.")
    endif()
  endforeach()

endfunction()
