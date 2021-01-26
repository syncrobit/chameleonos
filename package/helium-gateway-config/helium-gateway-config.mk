################################################################################
#
# helium-gateway-config
#
################################################################################

HELIUM_GATEWAY_CONFIG_VERSION = 2021.01.22.0
HELIUM_GATEWAY_CONFIG_SITE = $(call github,helium,gateway-config,$(HELIUM_GATEWAY_CONFIG_VERSION))
HELIUM_GATEWAY_CONFIG_LICENSE = Apache-2.0
HELIUM_GATEWAY_CONFIG_LICENSE_FILES = LICENSE
HELIUM_GATEWAY_CONFIG_DEPENDENCIES = dbus gmp libsodium erlang host-rust-bin host-erlang-rebar
            
#HELIUM_GATEWAY_CONFIG_POST_EXTRACT_HOOKS += HELIUM_GATEWAY_CONFIG_FETCH_PATCH_DEPS

define HELIUM_GATEWAY_CONFIG_FETCH_PATCH_DEPS
    (cd $(@D); \
            CC="$(TARGET_CC)" \
            CXX="$(TARGET_CXX)" \
            CFLAGS="$(TARGET_CFLAGS) -U__sun__" \
            CXXFLAGS="$(TARGET_CXXFLAGS)" \
            LDFLAGS="$(TARGET_LDFLAGS) -L $(STAGING_DIR)/usr/lib/erlang/lib/erl_interface-$(ERLANG_EI_VSN)/lib" \
            ERLANG_ROCKSDB_OPTS="-DWITH_BUNDLE_SNAPPY=ON -DWITH_BUNDLE_LZ4=ON" \
            ERL_COMPILER_OPTIONS="[deterministic]" \
            ERTS_INCLUDE_DIR="$(STAGING_DIR)/usr/lib/erlang/erts-10.6/include" \
            $(REBAR_TARGET_DEPS_ENV) \
            $(TARGET_MAKE_ENV) \
            CARGO_HOME=$(HOST_DIR)/share/cargo \
            CARGO_BUILD_TARGET=aarch64-unknown-linux-gnu \
            ./rebar3 get-deps \
    )
    
    patch -d $(@D)/_build/default/lib/erasure -p1 < package/helium-miner/erlang-erasure._patch
    patch -d $(@D)/_build/default/lib/erlang_pbc -p1 < package/helium-miner/erlang-pbc._patch
    patch -d $(@D)/_build/default/lib/procket -p1 < package/helium-miner/procket._patch
    patch -d $(@D)/_build/default/lib/rocksdb -p1 < package/helium-miner/erlang-rocksdb._patch
endef
            
define HELIUM_GATEWAY_CONFIG_BUILD_CMDS
    (cd $(@D); \
            CC="$(TARGET_CC)" \
            CXX="$(TARGET_CXX)" \
            CFLAGS="$(TARGET_CFLAGS) -U__sun__" \
            CXXFLAGS="$(TARGET_CXXFLAGS)" \
            LDFLAGS="$(TARGET_LDFLAGS) -L $(STAGING_DIR)/usr/lib/erlang/lib/erl_interface-$(ERLANG_EI_VSN)/lib" \
            $(REBAR_TARGET_DEPS_ENV) \
            $(TARGET_MAKE_ENV) \
            ./rebar3 as prod tar -n gateway_config \
    )
endef

define HELIUM_GATEWAY_CONFIG_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/opt/gateway_config; \
    cd $(TARGET_DIR)/opt/gateway_config; \
    tar -zxvf $(@D)/_build/prod/rel/*/*.tar.gz;
endef

define HELIUM_GATEWAY_CONFIG_INSTALL_STAGING_CMDS
endef

define HELIUM_GATEWAY_CONFIG_INSTALL_CMDS
endef

$(eval $(generic-package))
