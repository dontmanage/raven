#!bin/bash

set -e

if [[ -f "/workspaces/dontmanage_codespace/dontmanage-bench/apps/dontmanage" ]]
then
    echo "Bench already exists, skipping init"
    exit 0
fi

rm -rf /workspaces/dontmanage_codespace/.git

source /home/dontmanage/.nvm/nvm.sh
nvm alias default 18
nvm use 18

echo "nvm use 18" >> ~/.bashrc
cd /workspace

bench init \
--ignore-exist \
--skip-redis-config-generation \
dontmanage-bench

cd dontmanage-bench

# Use containers instead of localhost
bench set-mariadb-host mariadb
bench set-redis-cache-host redis-cache:6379
bench set-redis-queue-host redis-queue:6379
bench set-redis-socketio-host redis-socketio:6379

# Remove redis from Procfile
sed -i '/redis/d' ./Procfile


bench new-site dev.localhost \
--mariadb-root-password 123 \
--admin-password admin \
--no-mariadb-socket

bench --site dev.localhost set-config developer_mode 1
bench --site dev.localhost clear-cache
bench use dev.localhost
bench get-app https://github.com/The-Commit-Company/Raven.git
bench --site dev.localhost install-app raven