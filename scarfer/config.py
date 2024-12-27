# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os

scarfer_version = "0.5.5"
scarfer_name = "scarfer"

TOP_DIR = os.path.dirname(os.path.realpath(__file__))
VAR_DIR = os.path.join(TOP_DIR, "var")
DEFAULT_FILE_EXCLUDE_FILE = os.path.join(VAR_DIR, "default-exclude-files.txt")
