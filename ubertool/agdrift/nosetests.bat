#! /usr/bin/env bash #needs to know bash, python, or sh, etc.

#chmod +x filename to make this file executable, then
#bash filename to run

#nose2 -v

#run the tests and create an html report
nosetests tests/test_agdrift_unittest.py tests/test_agdrift_integration.py --with-html
