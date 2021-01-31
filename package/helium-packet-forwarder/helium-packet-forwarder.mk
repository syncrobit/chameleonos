################################################################################
#
# helium-packet-forwarder
#
################################################################################

HELIUM_PACKET_FORWARDER_VERSION = 2021.01.22.0
HELIUM_PACKET_FORWARDER_SITE = $(call github,helium,sx1302_hal,$(HELIUM_PACKET_FORWARDER_VERSION))
HELIUM_PACKET_FORWARDER_LICENSE = Apache-2.0
HELIUM_PACKET_FORWARDER_LICENSE_FILES = LICENSE
            
define HELIUM_PACKET_FORWARDER_BUILD_CMDS
    (cd $(@D); \
            CROSS_COMPILE=aarch64-none-linux-gnu- \
            $(TARGET_MAKE_ENV) \
            make \
    )
endef

define HELIUM_PACKET_FORWARDER_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/opt/packet_forwarder/bin
    mkdir -p $(TARGET_DIR)/opt/packet_forwarder/etc
    cp $(@D)/tools/reset_lgw.sh $(TARGET_DIR)/opt/packet_forwarder/bin
    cp $(@D)/packet_forwarder/lora_pkt_fwd $(TARGET_DIR)/opt/packet_forwarder/bin
    cp package/helium-packet-forwarder/global_conf.json $(TARGET_DIR)/opt/packet_forwarder/etc
endef

define HELIUM_PACKET_FORWARDER_INSTALL_STAGING_CMDS
endef

define HELIUM_PACKET_FORWARDER_INSTALL_CMDS
endef

$(eval $(generic-package))
