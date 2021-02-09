################################################################################
#
# python-pyatecc
#
################################################################################

PYTHON_PYATECC_VERSION = 99a2e602a9635eadc66d79823963058d02c259fa
PYTHON_PYATECC_SITE = $(call github,ccrisan,pyatecc,$(PYTHON_PYATECC_VERSION))
PYTHON_PYATECC_SETUP_TYPE = setuptools
PYTHON_PYATECC_LICENSE = MIT
PYTHON_PYATECC_LICENSE_FILES = LICENSE

$(eval $(python-package))
