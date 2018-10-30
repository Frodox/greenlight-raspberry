#!/bin/bash

readonly PI_USER="pi"
readonly SOURCE=$(readlink -f "$BASH_SOURCE")

if [[ "$(whoami)" == "root" ]];
then
    a=("/bin/bash" "$SOURCE" "$@")
    sudo -u $PI_USER -- "/usr/bin/nohup" "${a[@]}" &>/dev/null &
    exit 0
elif [[ "$(whoami)" == "$PI_USER" ]];
then
    # Ok
    :
fi

REMOTE_HOST=146.185.146.196
PROXY_PORT=${1:-}

case $(hostname) in
    *greenlight*)
        PROXY_PORT=${PROXY_PORT:-3005}
    ;;
    *lexx*)
        PROXY_PORT=${PROXY_PORT:-3007}
    ;;
    *)
        [[ -z "$PROXY_PORT" ]] && PROXY_PORT=$(shuf -i 3010-3020 -n 1)
    ;;
esac

# ждём перед первым запуском, иначе ping что-то повисает
echo "Waiting 30s to init network..."
sleep 30

while ! ping -W 10 -c 3 $REMOTE_HOST &>/dev/null; do
    sleep 10
done


# сеть пингуется, можно подключаться
while :;
do
    echo "Creating reverse tunnel on $PROXY_PORT port..."
    ssh \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    -N -T \
    -R $PROXY_PORT:localhost:22 \
    -R 5000:localhost:5000 \
    bit-tunnel

    sleep 30
done
