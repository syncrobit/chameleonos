#!/bin/bash

if [[ -z "$1" ]]; then
    echo "Usage: $0 <miner_version>"
    exit 1
fi

set -e
version=$1
url=https://github.com/helium/miner/archive/refs/tags/${version}.tar.gz
dest=/tmp/miner-${version}.tar.gz
root=$(dirname $0)
echo "downloading ${url}"
curl -sSL "${url}" -o ${dest}
sha=$(sha256sum ${dest} | cut -d ' ' -f 1)
echo "sha256 ${sha} helium-miner-${version}.tar.gz" > ${root}/package/helium-miner/helium-miner.hash
sed -ri "s/HELIUM_MINER_VERSION = .*/HELIUM_MINER_VERSION = ${version}/" ${root}/package/helium-miner/helium-miner.mk
(cd ${root}; git commit -am "miner: Update to ${version}")
