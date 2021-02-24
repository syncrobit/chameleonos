################################################################################
#
# cynogale
#
################################################################################

CYNOGALE_VERSION = 90c8a618515f29723ec9c6644dec0ef318fdd789
CYNOGALE_SITE = $(call github,syncrobit,cynogale,$(CYNOGALE_VERSION))
CYNOGALE_DEPENDENCIES = sqlite

define CYNOGALE_BUILD_CMDS
    make CC="$(TARGET_CC)" -C "$(@D)"
endef

define CYNOGALE_INSTALL_TARGET_CMDS
    cp $(@D)/cynogale $(TARGET_DIR)/usr/bin/
endef

$(eval $(generic-package))
