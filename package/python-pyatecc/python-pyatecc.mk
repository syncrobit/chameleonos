################################################################################
#
# python-pyatecc
#
################################################################################

PYTHON_PYATECC_VERSION = 5064a387fd38943baa333511d28c5800a6ca590f
PYTHON_PYATECC_SITE = $(call github,ccrisan,pyatecc,$(PYTHON_PYATECC_VERSION))
PYTHON_PYATECC_SETUP_TYPE = setuptools
PYTHON_PYATECC_LICENSE = MIT
PYTHON_PYATECC_LICENSE_FILES = LICENSE
PYTHON_PYATECC_DEPENDENCIES = python-smbus2

$(eval $(python-package))
