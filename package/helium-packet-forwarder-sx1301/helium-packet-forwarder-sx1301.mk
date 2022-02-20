################################################################################
#
# helium-packet-forwarder-sx1301
#
################################################################################

HELIUM_PACKET_FORWARDER_SX1301_VERSION = 2021.05.20.0
HELIUM_PACKET_FORWARDER_SX1301_SITE = $(call github,helium,packet_forwarder,$(HELIUM_PACKET_FORWARDER_SX1301_VERSION))
HELIUM_PACKET_FORWARDER_SX1301_LICENSE = Apache-2.0
HELIUM_PACKET_FORWARDER_SX1301_LICENSE_FILES = LICENSE
HELIUM_PACKET_FORWARDER_SX1301_CONF_OPTS = -DWITH_VENDORED_HAL=ON
HELIUM_PACKET_FORWARDER_SX1301_POST_EXTRACT_HOOKS += HELIUM_PACKET_FORWARDER_SX1301_POST_EXTRACT

define HELIUM_PACKET_FORWARDER_SX1301_POST_EXTRACT
    ( \
        cd $(@D) && \
        git clone git@github.com:helium/lora_gateway.git extern/lora_gateway && \
        cd extern/lora_gateway && \
        git checkout $(HELIUM_PACKET_FORWARDER_SX1301_VERSION) \
    )
    sed -ri 's/SPI_SPEED\s+1/SPI_SPEED 2/' $(@D)/extern/lora_gateway/libloragw/src/loragw_spi.native.c
endef

define HELIUM_PACKET_FORWARDER_SX1301_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/opt/packet_forwarder/bin
    mkdir -p $(TARGET_DIR)/opt/packet_forwarder/etc
    mkdir -p $(TARGET_DIR)/opt/packet_forwarder/lib
    ln -sf /usr/bin/reset_lgw.sh $(TARGET_DIR)/opt/packet_forwarder/bin
    cp $(@D)/lora_pkt_fwd/lora_pkt_fwd $(TARGET_DIR)/opt/packet_forwarder/bin/lora_pkt_fwd_sx1301
    cp $(@D)/extern/lora_gateway/libloragw/libloragw.so $(TARGET_DIR)/opt/packet_forwarder/lib
    cp package/helium-packet-forwarder-sx1301/global_conf.json.sx1301.* $(TARGET_DIR)/opt/packet_forwarder/etc/
    ln -sf /var/run/global_conf.json $(TARGET_DIR)/opt/packet_forwarder/bin/global_conf.json
endef

$(eval $(cmake-package))
