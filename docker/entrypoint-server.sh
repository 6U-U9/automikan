#!/bin/bash

chown -R ${PUID}:${PGID} /torrent
chown -R ${PUID}:${PGID} /data
chown -R ${PUID}:${PGID} /automikan
chown -R ${PUID}:${PGID} /server
chmod -R 755 /server
exec gosu ${PUID}:${PGID} python3 main.py