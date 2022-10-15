################################################################################
# Project:  Lib Psycopg
# Purpose:  CMake build scripts
# Author:   Dmitry Baryshnikov, dmitry.baryshnikov@nexgis.com
################################################################################
# Copyright (C) 2017-2018, NextGIS <info@nextgis.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
################################################################################
cmake_minimum_required(VERSION 2.8.12 FATAL_ERROR)

project(pyparsing)

if(NOT DEFINED PACKAGE_VENDOR)
    set(PACKAGE_VENDOR NextGIS)
endif()

if(NOT DEFINED PACKAGE_BUGREPORT)
    set(PACKAGE_BUGREPORT info@nextgis.com)
endif()

# some init settings
set(CMAKE_COLOR_MAKEFILE ON)
# set path to additional CMake modules
set(CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/cmake ${CMAKE_MODULE_PATH})

if(OSX_FRAMEWORK)
  set(INSTALL_LIB_DIR "Library" CACHE INTERNAL "Installation directory for libraries" FORCE)
else()
    set(INSTALL_LIB_DIR "." CACHE INTERNAL "Installation directory for libraries" FORCE)
endif()

find_program(PYTHON3_EXECUTABLE python3)
set(PYTHON_EXECUTABLE ${PYTHON3_EXECUTABLE})

find_package(PythonInterp 3)
if(NOT PYTHONINTERP_FOUND)
    message(FATAL_ERROR "Cannot find python")
endif()

file(DOWNLOAD "https://pypi.python.org/pypi/${PROJECT_NAME}/json" "${CMAKE_CURRENT_BINARY_DIR}/meta.json")

include(util)
get_compiler_version(COMPILER)
# get version and download url
execute_process(COMMAND ${PYTHON_EXECUTABLE}
    ${CMAKE_SOURCE_DIR}/cmake/pypi_process.py ${PLUGIN} ${CMAKE_CURRENT_BINARY_DIR}/meta.json ${COMPILER}
    OUTPUT_VARIABLE PACKAGE_DETAILS
    OUTPUT_STRIP_TRAILING_WHITESPACE
)

list(GET PACKAGE_DETAILS 0 DOWNLOAD_URL)
list(GET PACKAGE_DETAILS 1 VERSION)
list(GET PACKAGE_DETAILS 2 PROJECT_CPACK_FILENAME)

report_version(${PROJECT_NAME} ${VERSION})

if(OSX_FRAMEWORK)
    set(FLAGS "ARCHFLAGS=-arch x86_64")
elseif(WIN32)
    if(MSVC_VERSION EQUAL 1400)
        set(FLAGS ${FLAGS} "VS90COMNTOOLS=$ENV{VS80COMNTOOLS}")
    elseif(MSVC_VERSION EQUAL 1500)
        set(FLAGS ${FLAGS} "VS90COMNTOOLS=$ENV{VS90COMNTOOLS}")
    elseif(MSVC_VERSION EQUAL 1600)
        set(FLAGS ${FLAGS} "VS90COMNTOOLS=$ENV{VS100COMNTOOLS}")
    elseif(MSVC_VERSION EQUAL 1700)
        set(FLAGS ${FLAGS} "VS90COMNTOOLS=$ENV{VS110COMNTOOLS}")
    elseif(MSVC_VERSION EQUAL 1800)
        set(FLAGS ${FLAGS} "VS90COMNTOOLS=$ENV{VS120COMNTOOLS}")
    elseif(MSVC_VERSION EQUAL 1900)
        set(FLAGS ${FLAGS} "VS90COMNTOOLS=$ENV{VS140COMNTOOLS}")
    else() # 1912 - Need to copy vcvarsall.bat from VC\Auxiliary\Build to VC
        get_filename_component(_COMNTOOLS_PREFIX "${CMAKE_C_COMPILER}" PATH)
        get_filename_component(_COMNTOOLS_PREFIX "${_COMNTOOLS_PREFIX}" PATH)
        get_filename_component(_COMNTOOLS_PREFIX "${_COMNTOOLS_PREFIX}" PATH)
        get_filename_component(_COMNTOOLS_PREFIX "${_COMNTOOLS_PREFIX}" PATH)
        get_filename_component(_COMNTOOLS_PREFIX "${_COMNTOOLS_PREFIX}" PATH)
        get_filename_component(_COMNTOOLS_PREFIX "${_COMNTOOLS_PREFIX}" PATH)
        # get_filename_component(_COMNTOOLS_PREFIX "${_COMNTOOLS_PREFIX}" PATH)
        set(FLAGS ${FLAGS} "VS90COMNTOOLS=${_COMNTOOLS_PREFIX}")
    endif()
else()
    set(FLAGS "NextGIS=TRUE")
endif()

# Download tarbal
set(OUT_DIR_NAME ${PROJECT_NAME}-${VERSION})
set(OUT_NAME "${OUT_DIR_NAME}.tar.gz")

if(NOT EXISTS "${CMAKE_CURRENT_BINARY_DIR}/${OUT_NAME}")
    status_message("Download ${DOWNLOAD_URL}")
    file(DOWNLOAD "${DOWNLOAD_URL}" "${CMAKE_CURRENT_BINARY_DIR}/${OUT_NAME}"
        SHOW_PROGRESS
    )
endif()

# Extract archive
if(NOT EXISTS ${CMAKE_CURRENT_BINARY_DIR}/${OUT_DIR_NAME})
    status_message("Extract ${CMAKE_CURRENT_BINARY_DIR}/${OUT_NAME}")
    execute_process(COMMAND ${CMAKE_COMMAND} -E tar xzf ${CMAKE_CURRENT_BINARY_DIR}/${OUT_NAME})
endif()

if(NOT SKIP_INSTALL_LIBRARIES AND NOT SKIP_INSTALL_ALL )
    install(DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/${OUT_DIR_NAME}/pyparsing DESTINATION ${INSTALL_LIB_DIR}/Lib/site-packages/)
endif()

# Archiving ====================================================================
set(PACKAGE_NAME ${PROJECT_NAME})

set(CPACK_PACKAGE_NAME "${PACKAGE_NAME}")
set(CPACK_PACKAGE_VENDOR "${PACKAGE_VENDOR}")
set(CPACK_PACKAGE_VERSION "${VERSION}")
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "${PACKAGE_NAME} Installation")
set(CPACK_PACKAGE_RELOCATABLE TRUE)
set(CPACK_ARCHIVE_COMPONENT_INSTALL ON)
set(CPACK_GENERATOR "ZIP")
set(CPACK_MONOLITHIC_INSTALL ON)
set(CPACK_STRIP_FILES TRUE)

# Get cpack zip archive name
set(CPACK_PACKAGE_FILE_NAME ${PROJECT_CPACK_FILENAME})

include(CPack)
