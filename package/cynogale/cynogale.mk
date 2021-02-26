################################################################################
#
# cynogale
#
################################################################################

CYNOGALE_VERSION = a2072c88b13719fd6a2bc8ead563395909eb05e8
CYNOGALE_SITE = $(call github,syncrobit,cynogale,$(CYNOGALE_VERSION))
CYNOGALE_DEPENDENCIES = sqlite

define CYNOGALE_BUILD_CMDS
    make CC="$(TARGET_CC)" -C "$(@D)"
endef

define CYNOGALE_INSTALL_TARGET_CMDS
    cp $(@D)/cynogale $(TARGET_DIR)/usr/bin/
endef

$(eval $(generic-package))
