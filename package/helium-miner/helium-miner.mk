################################################################################
#
# helium-miner
#
################################################################################

HELIUM_MINER_VERSION = testnet_2022.03.25.0
HELIUM_MINER_SITE = $(call github,helium,miner,$(HELIUM_MINER_VERSION))
HELIUM_MINER_LICENSE = Apache-2.0
HELIUM_MINER_LICENSE_FILES = LICENSE
HELIUM_MINER_DEPENDENCIES = dbus gmp libsodium erlang host-rust-bin
            
HELIUM_MINER_POST_EXTRACT_HOOKS += HELIUM_MINER_FETCH_PATCH_DEPS
HELIUM_MINER_POST_EXTRACT_HOOKS += HELIUM_MINER_UPDATE_VERSION

define HELIUM_MINER_FETCH_PATCH_DEPS
    (cd $(@D); $(TARGET_MAKE_ENV) ./rebar3 get-deps)

    patch -d $(@D)/_build/default/lib/erasure -p1 < package/helium-miner/erlang-erasure._patch
    patch -d $(@D)/_build/default/lib/procket -p1 < package/helium-miner/procket._patch
    patch -d $(@D)/_build/default/lib/clique -p1 < package/helium-miner/clique._patch
endef

define HELIUM_MINER_UPDATE_VERSION
    sed -i 's/git}/"$(HELIUM_MINER_VERSION)"}/g' $(@D)/rebar.config
endef
            
define HELIUM_MINER_BUILD_CMDS
    (cd $(@D); ERTS_VERSION=$$(ls -d $(STAGING_DIR)/usr/lib/erlang/erts-* | head -n1 | xargs basename | grep -oE [0-9.]+); \
            CC="$(TARGET_CC)" \
            CXX="$(TARGET_CXX)" \
            CFLAGS="$(TARGET_CFLAGS) -U__sun__" \
            CXXFLAGS="$(TARGET_CXXFLAGS)" \
            LDFLAGS="$(TARGET_LDFLAGS) -L $(STAGING_DIR)/usr/lib/erlang/lib/erl_interface-$(ERLANG_EI_VSN)/lib" \
            ERLANG_ROCKSDB_OPTS="-DWITH_BUNDLE_SNAPPY=ON -DWITH_BUNDLE_LZ4=ON" \
            ERL_COMPILER_OPTIONS="[deterministic]" \
            ERTS_INCLUDE_DIR="$(STAGING_DIR)/usr/lib/erlang/erts-$${ERTS_VERSION}/include" \
            $(TARGET_MAKE_ENV) \
            CARGO_HOME=$(HOST_DIR)/share/cargo \
            CARGO_BUILD_TARGET=aarch64-unknown-linux-gnu \
            ./rebar3 as prod tar -n miner \
    )
endef

define HELIUM_MINER_INSTALL_TARGET_CMDS
    rm -rf $(TARGET_DIR)/opt/miner; \
    mkdir -p $(TARGET_DIR)/opt/miner; \
    cd $(TARGET_DIR)/opt/miner; \
    tar xvf $(@D)/_build/prod/rel/*/*.tar.gz; \
    cp $(@D)/config/testnet-sys.config $(TARGET_DIR)/opt/miner/releases/*/; \
    mkdir -p update; \
    wget https://snapshots.helium.wtf/genesis.mainnet -o update/genesis.mainnet; \
    wget https://snapshots.helium.wtf/genesis.testnet -o update/genesis.testnet; \
    cp $(TARGET_DIR)/usr/lib/erlang/bin/no_dot_erlang.boot .
    
    rm -rf $(TARGET_DIR)/opt/miner/$${HOME}
    cp $(@D)/config/com.helium.Miner.conf $(TARGET_DIR)/etc/dbus-1/system.d
endef

define HELIUM_MINER_INSTALL_STAGING_CMDS
endef

define HELIUM_MINER_INSTALL_CMDS
endef

$(eval $(generic-package))
