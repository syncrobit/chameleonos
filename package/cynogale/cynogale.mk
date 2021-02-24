################################################################################
#
# cynogale
#
################################################################################

CYNOGALE_VERSION = dfcb584d0aa33af9fe66869bdb33f61ecd86ad2d
CYNOGALE_SITE = $(call github,syncrobit,cynogale,$(CYNOGALE_VERSION))
CYNOGALE_DEPENDENCIES = sqlite

define CYNOGALE_BUILD_CMDS
    make CC="$(TARGET_CC)" -C "$(@D)"
endef

define CYNOGALE_INSTALL_TARGET_CMDS
    cp $(@D)/cynogale $(TARGET_DIR)/usr/bin/
endef

$(eval $(generic-package))
