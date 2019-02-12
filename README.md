# greenlight-raspberry

Code for Raspberry Pi for GreenLight Demo project

Входная точка: http://solceramic.ru/test.html
Отправляет POST-запросы сюда: http://<сервер>:5000/greenlight

## ТЗ

* [+] Малина принимает POST запросы на порту от сайта
* [+] Парсит данные, отдаёт их в лог
* [+] Малина подключается к WiFi (см `/etc/wpa_supplicant/wpa_supplicant.conf`)
* [+] Малина отдаёт по serial-порту инфу
* Исключение, если не подключён GPIO
----------------------------------------
Exception happened during processing of request from ('192.168.0.101', 56780)
Traceback (most recent call last):
  File "/usr/lib/python3.5/socketserver.py", line 313, in _handle_request_noblock
    self.process_request(request, client_address)
  File "/usr/lib/python3.5/socketserver.py", line 341, in process_request
    self.finish_request(request, client_address)
  File "/usr/lib/python3.5/socketserver.py", line 354, in finish_request
    self.RequestHandlerClass(request, client_address, self)
  File "/usr/lib/python3.5/socketserver.py", line 681, in __init__
    self.handle()
  File "/usr/lib/python3.5/http/server.py", line 422, in handle
    self.handle_one_request()
  File "/usr/lib/python3.5/http/server.py", line 410, in handle_one_request
    method()
  File "/opt/dummy-server.py", line 138, in do_GET
    self.show_logs()
  File "/opt/dummy-server.py", line 129, in show_logs
    self.wfile.write(b"</code>")
  File "/usr/lib/python3.5/socket.py", line 594, in write
    return self._sock.send(b)
BrokenPipeError: [Errno 32] Broken pipe
----------------------------------------

* journalctl - логи в отдельный файл мб? 
* Мониторинг доступности малины извне (blackbox)


## Raspberry and UART

* https://pinout.xyz/pinout/uart
** GPIO14 (pin 8)  - TxD0
** GPIO15 (pin 10) - RxD0
* https://www.raspberrypi.org/documentation/configuration/uart.md

The SoCs used on the Raspberry Pis have two built-in UARTs, a **PL011** and a **mini UART**.

By default, on Raspberry Pi 3 the **PL011 UART** is connected to the BT module, while the **mini UART** is used for Linux console output.

In Linux device terms, by default, `/dev/ttyS0` refers to the **mini UART**, and `/dev/ttyAMA0` refers to the **PL011**.

The Linux console can be re-enabled by adding `enable_uart=1` to `/boot/config.txt`. This also fixes the core_freq to 250Mhz (unless force_turbo is set, when it will fixed to 400Mhz), which means that the UART baud rate stays consistent

---

`pi3-disable-bt` disables the Bluetooth device and restores `UART0/ttyAMA0` to `GPIO14` and `GPIO15`. It is also necessary to disable the system service that initialises the modem so it doesn't use the UART: 
```
sudo systemctl disable hciuart
sudo systemctl stop serial-getty@ttyAMA0.service
sudo systemctl disable serial-getty@ttyAMA0.service
sudo systemctl stop serial-getty@ttyS0.service
sudo systemctl disable serial-getty@ttyS0.service

cat /boot/config.txt
...
enable_uart=1
dtoverlay=pi3-disable-bt
...
```

`/boot/cmdline.txt` --- remove `console=serial0,115200`

---
* `B115200` / `B9600`


## Алгоритм общение RPI - PLC

* https://www.devdungeon.com/content/working-binary-data-python

Обмен происходит пакетами (набор байт/команд). 

Максимальная длина пакета - 204 байта

* 1 байт - длинна передаваемого пакета в байтах (без первого)
* 3 байта - фиксированный заголовок `0х56 0х12 0х54` (три числа в шестнадцатиричной системе)
* 3 байта - адрес светильника - `0хAA 0хBB 0хCC` (три числа в шестнадцатиричной системе)
* 1 байт команды - `0x01` - команда задания яркости
* 1-192 байт данных - уровень яркости, заданный 16-тиричным числом
* Блок CRC32 суммы данных пакета (1 число на 4 байта)

1 байт - 8 бит. Значения 0 - 255


## Общение с счётчиком Энергомера CE102M-R5 по rs485-USB

Интерфейс общения: serial по rs485 выходу.
Покупаем RS485-USB переходник, подключаем к счётчику и малине.

Протокол обмена данными: 
* согласно ГОСТ: 7 бит, 1 бит чётности, 1 стартовый бит, 1 стоп-бит

https://www.ab-log.ru/forum/viewtopic.php?t=8&start=180#p28234


Обмен данными осуществляется в соответствии с ГОСТ Р МЭК 61107 2001 в режиме `С`. В качестве адреса устройства используется значение параметра `IDPAS`. Форматы данных для обмена по интерфейсам приведены в приложении Д.
