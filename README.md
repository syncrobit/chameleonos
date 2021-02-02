# What's ChameleonOS?

**ChameleonOS** is an operating system for the SyncroBit Chameleon miner, based on [thingOS](https://github.com/ccrisan/thingos).

# Building

    ./build.sh raspberrypi4arm64
    ./build.sh raspberrypi4arm64 mkimage

# Writing the OS Image

You'll the [`writeimage.sh`](https://github.com/ccrisan/chameleonos/blob/main/writeimage.sh) script. Alternatively, you can use any SD card image writing tool, after extracting the compressed image.

Use the following command to write the OS image onto your SD card with `writeimage.sh`:

    ./writeimage.sh -i /path/to/chameleonos-raspberrypi4arm64-${version}.img.xz -d /dev/sdX

After building the OS from source, you can find it at `output/raspberrypi4arm64/images`:

    ./writeimage.sh -i output/raspberrypi4arm64/images/chameleonos-raspberrypi4arm64.img -d /dev/sdX
