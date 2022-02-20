################################################################################
#
# helium-gateway-config
#
################################################################################

HELIUM_GATEWAY_CONFIG_VERSION = 2021.03.09.0
HELIUM_GATEWAY_CONFIG_SITE = $(call github,helium,gateway-config,$(HELIUM_GATEWAY_CONFIG_VERSION))
HELIUM_GATEWAY_CONFIG_LICENSE = Apache-2.0
HELIUM_GATEWAY_CONFIG_LICENSE_FILES = LICENSE
HELIUM_GATEWAY_CONFIG_DEPENDENCIES = dbus gmp libsodium erlang host-rust-bin
            
define HELIUM_GATEWAY_CONFIG_BUILD_CMDS
    (cd $(@D); \
            CC="$(TARGET_CC)" \
            CXX="$(TARGET_CXX)" \
            CFLAGS="$(TARGET_CFLAGS) -U__sun__" \
            CXXFLAGS="$(TARGET_CXXFLAGS)" \
            LDFLAGS="$(TARGET_LDFLAGS) -L $(STAGING_DIR)/usr/lib/erlang/lib/erl_interface-$(ERLANG_EI_VSN)/lib" \
            $(TARGET_MAKE_ENV) \
            ./rebar3 as prod tar -n gateway_config \
    )
endef

define HELIUM_GATEWAY_CONFIG_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/opt/gateway_config/log; \
    cd $(TARGET_DIR)/opt/gateway_config; \
    tar xvf $(@D)/_build/prod/rel/*/*.tar.gz
    
    rm -rf $(TARGET_DIR)/opt/gateway_config/$${HOME}
    cp $(@D)/config/com.helium.Config.conf $(TARGET_DIR)/etc/dbus-1/system.d
endef

define HELIUM_GATEWAY_CONFIG_INSTALL_STAGING_CMDS
endef

define HELIUM_GATEWAY_CONFIG_INSTALL_CMDS
endef

$(eval $(generic-package))
