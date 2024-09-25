#!/bin/bash

# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

for version in 1.0.0 2.0.0 3.0.0
do
    PYTHONPATH=. scarfer/__main__.py example-data/scancode/$version/cairo-1.16.0-scan.json -ls -cs
    RET=$?
    echo "$version $RET"
    if [ $RET -ne 0 ]
    then
        echo Failed example-data/scancode/$version/cairo-1.16.0-scan.json ;
        exit 1
    fi
done
    
