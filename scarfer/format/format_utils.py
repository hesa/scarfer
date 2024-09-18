# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

def summarize_license(license_list):
    l_list = []
    for le in license_list:
        l_list.append(f'( {le} )') # noqa: E201, E202
    return " AND ".join(l_list)
