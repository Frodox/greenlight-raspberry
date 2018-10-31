# greenlight-raspberry

Code for Raspberry Pi for GreenLight Demo project

Входная точка: http://solceramic.ru/test.html
Отправляет POST-запросы сюда: http://bitthinker.com:5000/greenlight

## ТЗ

* [+] Малина принимает POST запросы на порту от сайта
* [+] Парсит данные, отдаёт их в лог
* [+] Малина подключается к WiFi (см `/etc/wpa_supplicant/wpa_supplicant.conf`)
* Малина отдаёт по serial-порту инфу


## Raspberry and UART

* https://pinout.xyz/pinout/uart
** GPIO14 (pin 8)  - TxD0
** GPIO15 (pin 10) - RxD0
* https://www.raspberrypi.org/documentation/configuration/uart.md

The SoCs used on the Raspberry Pis have two built-in UARTs, a **PL011** and a **mini UART**.

By default, on Raspberry Pi 3 the **PL011 UART** is connected to the BT module, while the **mini UART** is used for Linux console output.

In Linux device terms, by default, `/dev/ttyS0` refers to the **mini UART**, and `/dev/ttyAMA0` refers to the **PL011**.

The Linux console can be re-enabled by adding `enable_uart=1` to `/boot/config.txt`. This also fixes the core_freq to 250Mhz (unless force_turbo is set, when it will fixed to 400Mhz), which means that the UART baud rate stays consistent

Disables the Bluetooth device and restores `UART0/ttyAMA0` to GPIOs 14 and 15. It is also necessary to disable the system service that initialises the modem so it doesn't use the UART: `sudo systemctl disable hciuart`.
```
...
dtoverlay=pi3-disable-bt
...
```

---
* `B115200` / `B9600`
