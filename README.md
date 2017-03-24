ESP8266 IOT Button
==================

![Photo](http://i.imgur.com/osWEN4Z.jpg)

This code is intended to be used with an ESP8266 flashed with MicroPython.

![Schematic](http://i.imgur.com/mnZ3CU8.png)

I used [esptool](https://github.com/espressif/esptool) to flash the MCU, and
[ampy](https://github.com/adafruit/ampy) to perform the initial upload of
`main.py`. After that, all other code uploads can be done using
[webrepl](https://github.com/micropython/webrepl)

To program, hold down S2 (the program button) while pressing S1 (the main
button). This will put turn the device into an access point you can connect to.
Look for an ssid that starts with "IOTBTN-". Then, use webrepl to connect to
the device (just open webrepl.html in your browser, it's all client-side code).

Use webrepl to upload a config.json file like so:

```json
{
  "ssid": "your-wifi-ssid",
  "password": "your-wifi-password",
  "broker": "mqtt-broker-ip",
  "topic": "example/topic/name"
}
```

Next time you press the button, the device will power up, publish the topic to
the broker, and will then go into deep-sleep mode. The first press will connect
using DHCP, and then save a static wifi config (this makes future connections a
bit faster). So, the first press will take longer than subsequent presses.
