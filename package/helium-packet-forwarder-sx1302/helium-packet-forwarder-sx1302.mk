################################################################################
#
# helium-packet-forwarder-sx1302
#
################################################################################

HELIUM_PACKET_FORWARDER_SX1302_VERSION = 2021.05.20.0
HELIUM_PACKET_FORWARDER_SX1302_SITE = $(call github,helium,sx1302_hal,$(HELIUM_PACKET_FORWARDER_SX1302_VERSION))
HELIUM_PACKET_FORWARDER_SX1302_LICENSE = Apache-2.0
HELIUM_PACKET_FORWARDER_SX1302_LICENSE_FILES = LICENSE
            
define HELIUM_PACKET_FORWARDER_SX1302_BUILD_CMDS
    (cd $(@D); \
            CROSS_COMPILE=aarch64-none-linux-gnu- \
            $(TARGET_MAKE_ENV) \
            make \
    )
endef

define HELIUM_PACKET_FORWARDER_SX1302_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/opt/packet_forwarder/bin
    mkdir -p $(TARGET_DIR)/opt/packet_forwarder/etc
    ln -sf /usr/bin/reset_lgw.sh $(TARGET_DIR)/opt/packet_forwarder/bin
    cp $(@D)/packet_forwarder/lora_pkt_fwd $(TARGET_DIR)/opt/packet_forwarder/bin/lora_pkt_fwd_sx1302
    cp $(@D)/util_chip_id/chip_id $(TARGET_DIR)/opt/packet_forwarder/bin
    cp $(@D)/util_net_downlink/net_downlink $(TARGET_DIR)/opt/packet_forwarder/bin
    cp package/helium-packet-forwarder-sx1302/global_conf.json.sx1302.* $(TARGET_DIR)/opt/packet_forwarder/etc/
    ln -sf /var/run/global_conf.json $(TARGET_DIR)/opt/packet_forwarder/bin/global_conf.json
endef

define HELIUM_PACKET_FORWARDER_SX1302_INSTALL_STAGING_CMDS
endef

define HELIUM_PACKET_FORWARDER_SX1302_INSTALL_CMDS
endef

$(eval $(generic-package))
