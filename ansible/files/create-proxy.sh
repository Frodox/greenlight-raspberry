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
APP_PORT=${2:-}
EXPORTER_PORT=${2:-}

case $(hostname) in
    *greenlight*)
        PROXY_PORT=${PROXY_PORT:-3005}
        APP_PORT=5000
        EXPORTER_PORT=8000
    ;;
    *lexx*)
        PROXY_PORT=${PROXY_PORT:-3008}
        APP_PORT=5001
        EXPORTER_PORT=8001
    ;;
    *)
        [[ -z "$PROXY_PORT" ]] && PROXY_PORT=$(shuf -i 3010-3020 -n 1)
        [[ -z "$APP_PORT" ]] && APP_PORT=$(shuf -i 3021-3031 -n 1)
        EXPORTER_PORT=8002
    ;;
esac

# ждём перед первым запуском, иначе ping что-то повисает
echo "Waiting 30s to init network..."
sleep 30

echo "Init modem e3131"
for i in eth0 eth1;
do

    echo "> Init $i"
    for index in 1 2 3;
    do
        sudo curl -s --interface $i ifconfig.io
        sleep 3
    done

done

while ! ping -W 10 -c 3 $REMOTE_HOST &>/dev/null; do
    sleep 10
done


# сеть пингуется, можно подключаться
while :;
do
    echo "Creating reverse tunnel on $PROXY_PORT port..."
    ping -W 10 -c 3 $REMOTE_HOST

    ssh \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    -o ExitOnForwardFailure=yes \
    -N -T -n \
    -R $PROXY_PORT:localhost:22 \
    -R $APP_PORT:localhost:5000 \
    -R $EXPORTER_PORT:localhost:8000 \
    -q \
    bit-tunnel

    echo "ssh disaconected. sleeping..."
    sleep 30
done
