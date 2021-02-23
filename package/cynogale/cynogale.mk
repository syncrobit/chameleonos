################################################################################
#
# cynogale
#
################################################################################

CYNOGALE_VERSION = b09138a4f25e89afc7705d95f539b7b9d83719e3
CYNOGALE_SITE = $(call github,syncrobit,cynogale,$(CYNOGALE_VERSION))
CYNOGALE_DEPENDENCIES = sqlite

define CYNOGALE_BUILD_CMDS
    make CC="$(TARGET_CC)" -C "$(@D)"
endef

define CYNOGALE_INSTALL_TARGET_CMDS
    cp $(@D)/cynogale $(TARGET_DIR)/usr/bin/
endef

$(eval $(generic-package))
