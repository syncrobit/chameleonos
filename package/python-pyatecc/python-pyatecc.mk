################################################################################
#
# python-pyatecc
#
################################################################################

PYTHON_PYATECC_VERSION = 399634c122835d894a3f2fdfa645830c736f3d38
PYTHON_PYATECC_SITE = $(call github,ccrisan,pyatecc,$(PYTHON_PYATECC_VERSION))
PYTHON_PYATECC_SETUP_TYPE = setuptools
PYTHON_PYATECC_LICENSE = MIT
PYTHON_PYATECC_LICENSE_FILES = LICENSE
PYTHON_PYATECC_DEPENDENCIES = python-smbus2

$(eval $(python-package))
