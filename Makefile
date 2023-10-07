# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

clean:
	find . -name "*~" | xargs rm 

py-check: py-lint py-test

py-test:
	PYTHONPATH=. python3 -m unittest

py-lint:
	flake8

reuse-lint:
	reuse --suppress-deprecation lint

lint: py-lint reuse-lint
