################################################################################
#
# helium-miner
#
################################################################################

HELIUM_MINER_VERSION = 2021.01.22.0
HELIUM_MINER_SITE = $(call github,helium,miner,$(HELIUM_MINER_VERSION))
HELIUM_MINER_LICENSE = Apache-2.0
HELIUM_MINER_LICENSE_FILES = LICENSE
HELIUM_MINER_USE_AUTOCONF = NO
HELIUM_MINER_USE_BUNDLED_REBAR = YES


define HELIUM_MINER_BUILD_CMDS
    echo RUSTFLAGS="-L$(@D)/_build/default/lib/erbloom/crates/bloom/target/release/deps";
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
            CARGO_BUILD_TARGET=arm-unknown-linux-gnueabihf \
            CARGO_HOME=$(HOST_DIR)/share/cargo \
            CARGO_TERM_VERBOSE=true \
            TARGET=arm-unknown-linux-gnueabihf \
            ./rebar3 as docker tar \
    )
endef

$(eval $(rebar-package))
