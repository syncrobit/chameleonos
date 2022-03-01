#!/bin/bash

mount -o remount,rw /
echo -e '#!/bin/bash\ngrep -q dtparam=ant2 $1/config.txt && echo dtparam=ant2 >> /boot/config.txt' > /usr/libexec/fw-restore-boot-cfg
chmod +x /usr/libexec/fw-restore-boot-cfg
