################################################################################
#
# rtl8821cu
#
################################################################################

RTL8821CU_VERSION = 7cff07cdfcbbc0b10ce669ffcef571ea5edf7d21
RTL8821CU_SITE = $(call github,ulli-kroll,rtl8821cu,$(RTL8821CU_VERSION))
RTL8821CU_LICENSE = GPL-2.0
RTL8821CU_LICENSE_FILES = LICENSE
RTL8821CU_DEPENDENCIES = linux linux-firmware

define RTL8821CU_BUILD_CMDS
    cd $(@D) && make KSRC=$(LINUX_DIR) ARCH=arm64 CROSS_COMPILE=$(TARGET_CROSS)
endef

define RTL8821CU_INSTALL_TARGET_CMDS
	$(LINUX_MAKE_ENV) $(MAKE) \
		-C $(LINUX_DIR) \
		$(LINUX_MAKE_FLAGS) \
		PWD=$(@D)/$(d) \
		M=$(@D)/$(d) \
		modules_install
    mkdir -p $(TARGET_DIR)/lib/firmware/rtl_bt
    cp $(BUILD_DIR)/linux-firmware-*/rtl_bt/rtl8821*.bin $(TARGET_DIR)/lib/firmware/rtl_bt
endef

$(eval $(generic-package))
