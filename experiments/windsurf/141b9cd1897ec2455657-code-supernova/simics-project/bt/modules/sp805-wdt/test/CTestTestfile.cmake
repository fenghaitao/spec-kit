# CMake generated Testfile for 
# Source directory: /home/hfeng1/latest-windsurf/simics-project/modules/sp805-wdt/test
# Build directory: /home/hfeng1/latest-windsurf/simics-project/bt/modules/sp805-wdt/test
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test([=[sp805-wdt::sp805-wdt]=] "/home/hfeng1/latest-windsurf/simics-project/simics" "--batch-mode" "s-sp805-wdt.py")
set_tests_properties([=[sp805-wdt::sp805-wdt]=] PROPERTIES  DEF_SOURCE_LINE "/home/hfeng1/latest-windsurf/simics-project/modules/sp805-wdt/test/s-sp805-wdt.py:1" ENVIRONMENT_MODIFICATION "SANDBOX=set:/home/hfeng1/latest-windsurf/simics-project/bt/modules/sp805-wdt/test/sandbox" WORKING_DIRECTORY "/home/hfeng1/latest-windsurf/simics-project/modules/sp805-wdt/test" _BACKTRACE_TRIPLES "/home/hfeng1/.simics-mcp-server/simics-install/simics-7.57.0/cmake/simics/Simics.cmake;1441;add_test;/home/hfeng1/latest-windsurf/simics-project/modules/sp805-wdt/test/CMakeLists.txt;4;simics_add_test;/home/hfeng1/latest-windsurf/simics-project/modules/sp805-wdt/test/CMakeLists.txt;0;")
add_test([=[sp805-wdt::info-status]=] "/home/hfeng1/latest-windsurf/simics-project/simics" "--batch-mode" "s-info-status.py")
set_tests_properties([=[sp805-wdt::info-status]=] PROPERTIES  DEF_SOURCE_LINE "/home/hfeng1/latest-windsurf/simics-project/modules/sp805-wdt/test/s-info-status.py:1" ENVIRONMENT_MODIFICATION "SANDBOX=set:/home/hfeng1/latest-windsurf/simics-project/bt/modules/sp805-wdt/test/sandbox" WORKING_DIRECTORY "/home/hfeng1/latest-windsurf/simics-project/modules/sp805-wdt/test" _BACKTRACE_TRIPLES "/home/hfeng1/.simics-mcp-server/simics-install/simics-7.57.0/cmake/simics/Simics.cmake;1441;add_test;/home/hfeng1/latest-windsurf/simics-project/modules/sp805-wdt/test/CMakeLists.txt;5;simics_add_test;/home/hfeng1/latest-windsurf/simics-project/modules/sp805-wdt/test/CMakeLists.txt;0;")
