# Советы и практики по работе с образом raspbian

* Посмотреть адрес вставленной SD-карты.
```
# dmesg -T --color=always|tail -n 30
# lsblk 
```
* [Скачать свежий образ Raspbian](https://downloads.raspberrypi.org/raspbian_lite_latest)


## Запись образа на малину

1. `unzip -p 2018-10-09-raspbian-stretch-lite.zip | bs=4M conv=fsync status=progress dd of=/dev/sde`
1. `dd bs=4M if=raspbian.img of=/dev/sde`
1. `gunzip --stdout raspbian.img.gz | dd bs=4M of=/dev/sde`

## Бэкап с малины

### Regular

```bash
dd bs=4M of=raspbian-$(date +%F).img status=progress if=/dev/sde
```

Образ получится по весу == размеру SD карты, хотя занята может быть лишь часть.

### Gziped

```
dd bs=4M if=/dev/sde | gzip > raspbian-$(date +%F).img.gz
```
