################################################################################
#
# cynogale
#
################################################################################

CYNOGALE_VERSION = 44e0ab798b495537fb5abf59e4c0a30b8813d49c
CYNOGALE_SITE = $(call github,syncrobit,cynogale,$(CYNOGALE_VERSION))
CYNOGALE_DEPENDENCIES = sqlite

define CYNOGALE_BUILD_CMDS
    make CC="$(TARGET_CC)" -C "$(@D)"
endef

define CYNOGALE_INSTALL_TARGET_CMDS
    cp $(@D)/cynogale $(TARGET_DIR)/usr/bin/
endef

$(eval $(generic-package))
