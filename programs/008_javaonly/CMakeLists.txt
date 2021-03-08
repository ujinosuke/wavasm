project(test_project)
set(CMAKE_C_FLAGS "-s WASM=0")
set(CMAKE_CXX_FLAGS "-s WASM=0")

add_executable(index hello.c foo.c)
