set(SECURE_CXX_FLAGS "")
if ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
    set(SECURE_CXX_FLAGS "-fstack-protector-all -Wl,-z,relro,-z,now,-z,noexecstack")
endif()
set(_ms_tmp_CMAKE_CXX_FLAGS_F ${CMAKE_CXX_FLAGS})
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fvisibility=hidden")

include(cmake/utils.cmake)
include(${CMAKE_SOURCE_DIR}/cmake/external_libs/eigen.cmake)
include(${CMAKE_SOURCE_DIR}/cmake/external_libs/json.cmake)
include(${CMAKE_SOURCE_DIR}/cmake/dependency_securec.cmake)
include(${CMAKE_SOURCE_DIR}/cmake/external_libs/protobuf.cmake)
include(${CMAKE_SOURCE_DIR}/cmake/external_libs/pybind11.cmake)
MESSAGE("go to link flatbuffers")
include(${CMAKE_SOURCE_DIR}/cmake/external_libs/flatbuffers.cmake)
if(USE_GLOG)
    include(${CMAKE_SOURCE_DIR}/cmake/external_libs/glog.cmake)
endif()

find_package(Python3)
include_directories(${Python3_INCLUDE_DIRS})
include_directories(${CMAKE_SOURCE_DIR}/third_party)
if (ENABLE_CPU)
    include(${CMAKE_SOURCE_DIR}/cmake/external_libs/mkl_dnn.cmake)
endif()

if (ENABLE_GPU)
    include(${CMAKE_SOURCE_DIR}/cmake/external_libs/dlpack.cmake)
    include(${CMAKE_SOURCE_DIR}/cmake/external_libs/dmlc_core.cmake)
    include(${CMAKE_SOURCE_DIR}/cmake/external_libs/rang.cmake)
    include(${CMAKE_SOURCE_DIR}/cmake/external_libs/tvm_gpu.cmake)

    if (ENABLE_MPI)
        include(${CMAKE_SOURCE_DIR}/cmake/external_libs/nccl.cmake)
        include(${CMAKE_SOURCE_DIR}/cmake/external_libs/ompi.cmake)
    endif()
endif()

if (ENABLE_GE)
    include_directories(${CMAKE_SOURCE_DIR}/third_party/ge/include)
    include_directories(${CMAKE_SOURCE_DIR}/third_party/ge/include/external)
    include_directories(${CMAKE_SOURCE_DIR}/third_party/ge/include/external/graph)
elseif(ENABLE_D OR ENABLE_TESTCASES)
    include_directories(${CMAKE_SOURCE_DIR}/graphengine/inc)
    include_directories(${CMAKE_SOURCE_DIR}/graphengine/inc/ops)
    include_directories(${CMAKE_SOURCE_DIR}/graphengine/inc/external)
    include_directories(${CMAKE_SOURCE_DIR}/graphengine/inc/external/graph)
endif()

if (ENABLE_MINDDATA)
    include(${CMAKE_SOURCE_DIR}/cmake/external_libs/jpeg_turbo.cmake)
    include(${CMAKE_SOURCE_DIR}/cmake/external_libs/libtiff.cmake)
    include(${CMAKE_SOURCE_DIR}/cmake/external_libs/opencv.cmake)
    include(${CMAKE_SOURCE_DIR}/cmake/external_libs/sqlite.cmake)
endif()

include(${CMAKE_SOURCE_DIR}/cmake/external_libs/gtest.cmake)
include(${CMAKE_SOURCE_DIR}/cmake/external_libs/onnx.cmake)
set(CMAKE_CXX_FLAGS ${_ms_tmp_CMAKE_CXX_FLAGS_F})
