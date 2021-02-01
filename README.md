# What's ChameleonOS?

**ChameleonOS** is an operating system for the SyncroBit Chameleon miner, based on [thingOS](https://github.com/ccrisan/thingos).

# Building

    ./build.sh raspberrypi4arm64
    ./build.sh raspberrypi4arm64 mkimage

# Writing the OS Image

Use the `writeimage.sh` to write the OS image onto your SD card:

    ./writeimage.sh -i output/raspberrypi4arm64/images/chameleonos-raspberrypi4arm64.img -d /dev/sdX
