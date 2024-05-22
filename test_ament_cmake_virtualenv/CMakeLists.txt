cmake_minimum_required(VERSION 3.5)
project(test_ament_cmake_virtualenv)

# Default to C++14
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

find_package(ament_cmake_virtualenv REQUIRED)
ament_generate_virtualenv(PYTHON_VERSION 3)

#ament_python_install_module(test_ament_cmake_virtualenv/test_ament_cmake_virtualenv-as_module.py)
#ament_python_install_package(test_ament_cmake_virtualenv/as_package)

install(FILES requirements.txt
  DESTINATION ${CMAKE_INSTALL_PREFIX}/share/${PROJECT_NAME})

if(BUILD_TESTING)
    # find_package(ament_cmake_haros REQUIRED)
    # ament_haros()
endif()

ament_package()
