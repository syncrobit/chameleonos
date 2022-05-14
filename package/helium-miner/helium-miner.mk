################################################################################
#
# helium-miner
#
################################################################################

HELIUM_MINER_VERSION = 2022.05.14.0
HELIUM_MINER_SITE = $(call github,helium,miner,$(HELIUM_MINER_VERSION))
HELIUM_MINER_LICENSE = Apache-2.0
HELIUM_MINER_LICENSE_FILES = LICENSE
HELIUM_MINER_DEPENDENCIES = dbus gmp libsodium erlang host-rust-bin
            
HELIUM_MINER_POST_EXTRACT_HOOKS += HELIUM_MINER_FETCH_PATCH_DEPS
HELIUM_MINER_POST_EXTRACT_HOOKS += HELIUM_MINER_UPDATE_VERSION

HELIUM_MINER_BUILD_AS = prod

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
    (cd $(@D); \
            CARGO_HOME=$(HOST_DIR)/share/cargo \
            CARGO_BUILD_TARGET=aarch64-unknown-linux-gnu \
            RUSTFLAGS="-C target-feature=-crt-static" \
            $(TARGET_MAKE_ENV) \
            $(MAKE) external_svcs \
    )
    (cd $(@D); ERTS_VERSION=$$(ls -d $(STAGING_DIR)/usr/lib/erlang/erts-* | head -n1 | xargs basename | grep -oE [0-9.]+); \
            CC="$(TARGET_CC)" \
            CXX="$(TARGET_CXX)" \
            CFLAGS="$(TARGET_CFLAGS) -U__sun__" \
            CXXFLAGS="$(TARGET_CXXFLAGS)" \
            LDFLAGS="$(TARGET_LDFLAGS) -L $(STAGING_DIR)/usr/lib/erlang/lib/erl_interface-$(ERLANG_EI_VSN)/lib" \
            ERLANG_ROCKSDB_OPTS="-DWITH_BUNDLE_SNAPPY=ON -DWITH_BUNDLE_LZ4=ON" \
            ERL_COMPILER_OPTIONS="[deterministic]" \
            ERTS_INCLUDE_DIR="$(STAGING_DIR)/usr/lib/erlang/erts-$${ERTS_VERSION}/include" \
            CARGO_HOME=$(HOST_DIR)/share/cargo \
            CARGO_BUILD_TARGET=aarch64-unknown-linux-gnu \
            RUSTFLAGS="-C target-feature=-crt-static" \
            $(TARGET_MAKE_ENV) \
            ./rebar3 as $(HELIUM_MINER_BUILD_AS) tar -n miner -v $(HELIUM_MINER_VERSION) \
    )
endef

define HELIUM_MINER_INSTALL_TARGET_CMDS
    rm -rf $(TARGET_DIR)/opt/miner; \
    mkdir -p $(TARGET_DIR)/opt/miner; \
    cd $(TARGET_DIR)/opt/miner; \
    tar xvf $(@D)/_build/$(HELIUM_MINER_BUILD_AS)/rel/miner/*.tar.gz; \
    cp $(@D)/config/testnet-sys.config $(TARGET_DIR)/opt/miner/releases/*/; \
    mkdir -p update; \
    wget https://snapshots.helium.wtf/genesis.mainnet -O update/genesis.mainnet; \
    wget https://snapshots.helium.wtf/genesis.testnet -O update/genesis.testnet; \
    cp $(TARGET_DIR)/usr/lib/erlang/bin/no_dot_erlang.boot .
    
    rm -rf $(TARGET_DIR)/opt/miner/$${HOME}
    rm -rf $(TARGET_DIR)/etc/helium_gateway
    cp $(@D)/config/com.helium.Miner.conf $(TARGET_DIR)/etc/dbus-1/system.d
endef

define HELIUM_MINER_INSTALL_STAGING_CMDS
endef

define HELIUM_MINER_INSTALL_CMDS
endef

define HELIUM_MINER_TOOLCHAIN_ADJUST_GCC_CMDS
    # On radxacm3 (default ARM toolchain), compiler is called aarch64-none-linux-gnu-gcc,
    # but external/gateway-rs/longfi-sys expects aarch64-linux-gnu-gcc.
    test -f $(HOST_DIR)/bin/aarch64-none-linux-gnu-gcc && \
        ln -s aarch64-none-linux-gnu-gcc $(HOST_DIR)/bin/aarch64-linux-gnu-gcc || true
    test -f $(HOST_DIR)/opt/ext-toolchain/bin/aarch64-none-linux-gnu-gcc && \
        ln -sf aarch64-none-linux-gnu-gcc $(HOST_DIR)/opt/ext-toolchain/bin/aarch64-linux-gnu-gcc || true
endef

TOOLCHAIN_POST_INSTALL_TARGET_HOOKS += HELIUM_MINER_TOOLCHAIN_ADJUST_GCC_CMDS

$(eval $(generic-package))
