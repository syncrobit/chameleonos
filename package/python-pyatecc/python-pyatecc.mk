################################################################################
#
# python-pyatecc
#
################################################################################

PYTHON_PYATECC_VERSION = d62468d70f986bd8dcff2b93f063c19201ee5483
PYTHON_PYATECC_SITE = $(call github,ccrisan,pyatecc,$(PYTHON_PYATECC_VERSION))
PYTHON_PYATECC_SETUP_TYPE = setuptools
PYTHON_PYATECC_LICENSE = MIT
PYTHON_PYATECC_LICENSE_FILES = LICENSE
PYTHON_PYATECC_DEPENDENCIES = python-smbus2

$(eval $(python-package))
