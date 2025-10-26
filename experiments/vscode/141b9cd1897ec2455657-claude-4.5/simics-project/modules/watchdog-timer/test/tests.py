# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""
Watchdog Timer Test Suite Registration

Registers all test scripts with the Simics test framework.
"""

def tests(suite):
    """Register all watchdog timer test scripts"""
    suite.add_simics_test("s-basic-registers.py")
    suite.add_simics_test("s-countdown.py")
    suite.add_simics_test("s-interrupt.py")
    suite.add_simics_test("s-reset.py")
    suite.add_simics_test("s-lock.py")
    suite.add_simics_test("s-integration-test.py")
    suite.add_simics_test("s-checkpoint.py")
