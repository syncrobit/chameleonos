################################################################################
#
# helium-gateway-mfr
#
################################################################################

HELIUM_GATEWAY_MFR_VERSION = bd523a1f80fc262b930a1cda98229dd10215a885
HELIUM_GATEWAY_MFR_SITE = $(call github,helium,gateway_mfr,$(HELIUM_GATEWAY_MFR_VERSION))
HELIUM_GATEWAY_MFR_LICENSE = Apache-2.0
HELIUM_GATEWAY_MFR_LICENSE_FILES = LICENSE
HELIUM_GATEWAY_MFR_DEPENDENCIES = erlang
            
HELIUM_GATEWAY_MFR_POST_EXTRACT_HOOKS += HELIUM_GATEWAY_MFR_FETCH_PATCH_DEPS

define HELIUM_GATEWAY_MFR_FETCH_PATCH_DEPS
    (cd $(@D); \
            CC="$(TARGET_CC)" \
            CXX="$(TARGET_CXX)" \
            CFLAGS="$(TARGET_CFLAGS) -U__sun__" \
            CXXFLAGS="$(TARGET_CXXFLAGS)" \
            LDFLAGS="$(TARGET_LDFLAGS) -L $(STAGING_DIR)/usr/lib/erlang/lib/erl_interface-$(ERLANG_EI_VSN)/lib" \
            $(TARGET_MAKE_ENV) \
            ./rebar3 get-deps \
    )

    patch -d $(@D)/_build/default/lib/ecc508 -p1 < package/helium-gateway-mfr/ecc508._patch
endef
            
define HELIUM_GATEWAY_MFR_BUILD_CMDS
    (cd $(@D); \
            CC="$(TARGET_CC)" \
            CXX="$(TARGET_CXX)" \
            CFLAGS="$(TARGET_CFLAGS) -U__sun__" \
            CXXFLAGS="$(TARGET_CXXFLAGS)" \
            LDFLAGS="$(TARGET_LDFLAGS) -L $(STAGING_DIR)/usr/lib/erlang/lib/erl_interface-$(ERLANG_EI_VSN)/lib" \
            $(TARGET_MAKE_ENV) \
            ./rebar3 as prod tar -n gateway_mfr \
    )
endef

define HELIUM_GATEWAY_MFR_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/opt/gateway_mfr/log; \
    cd $(TARGET_DIR)/opt/gateway_mfr; \
    tar xvf $(@D)/_build/prod/rel/*/*.tar.gz; \
    cp $(TARGET_DIR)/usr/lib/erlang/bin/no_dot_erlang.boot .
    
    rm -rf $(TARGET_DIR)/opt/gateway_mfr/$${HOME}
endef

$(eval $(generic-package))
