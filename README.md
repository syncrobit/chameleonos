# What's ChameleonOS?

**ChameleonOS** is an OS developed by SyncroB.it for various Helium miners, based on [thingOS](https://github.com/ccrisan/thingos).

# Building

## Preparing an OS image for development/testing purposes

    ./build-all.sh raspberrypi64
    sudo ./build.sh raspberrypi64 mkimage
    ./build.sh raspberrypi64 mkrelease

## Building OS images for all available vendors

    VERSION=2022.03.14.0 ./build-all.sh

# Deploying

If you want to deploy for specific vendors instead of all, specify the list of vendors in the `VENDORS` env variable.

## Uploading images to download server

    VERSION=2022.03.14.0 ./deploy-all.sh upload
    
## Promoting a version to beta

    VERSION=2022.03.14.0 ./deploy-all.sh promote-beta

## Promoting a version to stable

    VERSION=2022.03.14.0 ./deploy-all.sh promote-stable

# Writing the OS Image

You'll the [`writeimage.sh`](https://github.com/syncrobit/chameleonos/blob/main/writeimage.sh) script. Alternatively, you can use any SD card image writing tool, after extracting the compressed image.

Use the following command to write the OS image onto your SD card with `writeimage.sh`:

    ./writeimage.sh -i /path/to/chameleonos-${prefix}-${platform}-${version}.img.xz -d /dev/sdX

After building the OS from source, you can find it in `output/${platform}/images`.
