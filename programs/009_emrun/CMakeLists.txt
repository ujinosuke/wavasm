cmake_minimum_required(VERSION 3.0)
project(test_project)
add_link_options("--emrun")
add_executable(index hello.c)
