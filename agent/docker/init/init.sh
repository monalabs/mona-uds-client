#!/bin/bash
# This script is required in order to reset the hostpath folder where the UNIX Domain sockets will reside.
chmod -R 777 /var/run/mona
rm -f /var/run/mona/*sock*
