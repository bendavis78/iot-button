import utime as time
import ujson as json
import ubinascii as binascii
import network
import machine
from machine import Pin
from umqtt.simple import MQTTClient

script_start = time.ticks_ms()
CLIENT_ID = binascii.hexlify(machine.unique_id()).decode('utf-8')

# load config
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# set up pins
led = Pin(2, Pin.OUT, value=0)

# To enable config mode (webrepl), connect GPIO0 to GND via 10K resistor
config_mode_enabled = Pin(0, Pin.IN).value() == 0


def run():
    print('starting up...')

    # turn led on
    led.low()

    if config_mode_enabled:
        run_config_mode()
    else:
        run_action()

    # turn led off
    led.high()


def finish():
    print("total runtime: {}ms".format(time.ticks_ms() - script_start))

    if not config_mode_enabled:
        print("sleeping...")
        machine.deepsleep()


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    static = None

    try:
        with open('static.cfg', 'r') as static_cfg:
            print('found static config')
            static = static_cfg.read().strip().split('\n')
            if len(static) < 4:
                static = None
    except OSError:
        pass

    if static:
        print('using static config: ', static)
        wlan.ifconfig(static)

    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(config['ssid'], config['password'])
        while not wlan.isconnected():
            pass

    if static is None:
        # save wifi config for faster reconnection
        ifconfig = '\n'.join(wlan.ifconfig())
        with open('static.cfg', 'w') as static_cfg:
            print('Saving static config')
            static_cfg.write(ifconfig)


def run_config_mode():
    import webrepl
    ap = network.WLAN(network.AP_IF)
    ap_essid = config.get('ap_essid', 'IOTBTN-{}'.format(CLIENT_ID))
    ap_password = config.get('ap_password', 'iotbutton')
    ap.config(essid=ap_essid, password=ap_password)
    webrepl.start()
    print('ESSID: {}\nPASS: {}'.format(ap_essid, ap_password))


def run_action():
    connect_wifi()
    print('connecting to broker: {}'.format(config['broker']))
    broker = config['broker']
    topic = config.get('topic', 'button/{}'.format(CLIENT_ID.lower()))
    client = MQTTClient(CLIENT_ID, broker)
    client.connect()
    print('publishing topic: {} "pressed"'.format(topic))
    client.publish(topic, 'pressed')
    client.disconnect()


try:
    run()
finally:
    finish()
