################################################################################
#
# helium-gateway-mfr-rs
#
################################################################################

HELIUM_GATEWAY_MFR_RS_VERSION = v0.2.0
HELIUM_GATEWAY_MFR_RS_SITE = $(call github,helium,gateway-mfr-rs,$(HELIUM_GATEWAY_MFR_RS_VERSION))
HELIUM_GATEWAY_MFR_RS_LICENSE = Apache-2.0
HELIUM_GATEWAY_MFR_RS_LICENSE_FILES = LICENSE

HELIUM_GATEWAY_MFR_RS_DEPENDENCIES = host-rust-bin
HELIUM_GATEWAY_MFR_RS_CARGO_ENV = \
	CARGO_HOME=$(HOST_DIR)/share/cargo \
	CARGO_TARGET_APPLIES_TO_HOST="false"
HELIUM_GATEWAY_MFR_RS_CARGO_OPTS = \
	--target=$(RUSTC_TARGET_NAME) \
	--manifest-path=$(@D)/Cargo.toml \
	--release
HELIUM_GATEWAY_MFR_RS_BIN_DIR = target/$(RUSTC_TARGET_NAME)/release


define HELIUM_GATEWAY_MFR_RS_BUILD_CMDS
    cd $(@D) && $(TARGET_MAKE_ENV) $(HELIUM_GATEWAY_MFR_RS_CARGO_ENV) cargo build $(HELIUM_GATEWAY_MFR_RS_CARGO_OPTS)
endef

define HELIUM_GATEWAY_MFR_RS_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/$(HELIUM_GATEWAY_MFR_RS_BIN_DIR)/gateway_mfr $(TARGET_DIR)/usr/bin/gatewaymfr
    $(TARGET_CROSS)strip $(TARGET_DIR)/usr/bin/gatewaymfr
endef

$(eval $(generic-package))
