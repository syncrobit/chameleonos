if [ -s /var/run/public_keys ]; then
    echo "Hotspot name:   " $(cut -d '"' -f 6 < /var/run/public_keys)
    echo "Hotspot address:" $(cut -d '"' -f 2 < /var/run/public_keys)
fi
