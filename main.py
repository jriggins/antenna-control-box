try:
  from machine import Pin
except:
  class Pin:
    OUT = "OUT"

    def __init__(self, id_, mode=-1, pull=-1):
      print(f"Mocking pin {id_}")
      self._id = id_
      self._value = None

    def value(self, value_to_set=None):
      if value_to_set is not None:
        print(f"Setting pin {self._id} to {value_to_set}")
        self._value = value_to_set
      else:
        return self._value

    def __str__(self):
      return str({
        "id": self._id,
        "value": self.value
      })

try:
  import network

  wlan = network.WLAN(network.STA_IF)
  wlan.active(True)
  wlan.connect("Family Room","3614827555")       # ssid, password

  # connect the network
  wait = 10
  while wait > 0:
      if wlan.status() < 0 or wlan.status() >= 3:
          break
      wait -= 1
      print('waiting for connection...')
      time.sleep(1)

  # Handle connection error
  if wlan.status() != 3:
      raise RuntimeError('wifi connection failed')
  else:
      print('connected')
      ip=wlan.ifconfig()[0]
      print('IP: ', ip)
except:
  print("Did not connect to WLAN. Assuming running local")

import time
import re
try:
  import usocket as socket
except:
  import socket

class Brake:
  def __init__(self, relay):
    self._relay = relay
    self._name = "Brake"

  def is_enabled(self):
    return self._relay.value() == 0

  def enable(self):
    print(f"Enabling {self._name}")
    self._relay.value(0)

  def disable(self):
    print(f"Disabling {self._name}")
    self._relay.value(1)

  def __str__(self):
    return str({
      "relay": str(self._relay),
      "name": self._name,
    })


class Rotor:
  def __init__(self, relay, name):
    self._relay = relay
    self._name = name

  def is_enabled(self):
    return self._relay.value() == 0

  def enable(self):
    print(f"Enabling {self._name}")
    self._relay.value(0)

  def disable(self):
    print(f"Disabling {self._name}")
    self._relay.value(1)

  def __str__(self):
    return str({
      "relay": str(self._relay),
      "name": self._name,
    })


class ControlBox:
  def __init__(self, brake_pause_time_in_seconds=4.0):
    self._brake = Brake(relay=Pin(2,Pin.OUT))
    self._ccw_rotor = Rotor(relay=Pin(3,Pin.OUT,1), name="CCW")
    self._cw_rotor = Rotor(relay=Pin(4,Pin.OUT,1), name="CW")
    self._brake_pause_time_in_seconds = brake_pause_time_in_seconds

  def is_ccw_rotor_enabled(self):
    return self._ccw_rotor.is_enabled()

  def is_cw_rotor_enabled(self):
    return self._cw_rotor.is_enabled()

  def is_brake_enabled(self):
    return self._brake.is_enabled()

  def _sleep(self, sleep_seconds):
    print(f"Pausing for {sleep_seconds} seconds")
    time.sleep(sleep_seconds)

  def rotate_antenna_counter_clockwise(self):
    self._cw_rotor.disable()
    self._brake.disable()
    self._sleep(self._brake_pause_time_in_seconds)
    self._ccw_rotor.enable()

  def rotate_antenna_clockwise(self):
    self._ccw_rotor.disable()
    self._brake.disable()
    self._sleep(self._brake_pause_time_in_seconds)
    self._cw_rotor.enable()

  def stop_antenna_rotation(self):
    self._ccw_rotor.disable()
    self._cw_rotor.disable()
    self._sleep(self._brake_pause_time_in_seconds)
    self._brake.enable()

  def __str__(self):
    return str({
      "brake": str(self._brake),
      "ccw_rotor": str(self._ccw_rotor),
      "cw_rotor": str(self._cw_rotor),
      "brake_pause_time_in_seconds": self._brake_pause_time_in_seconds
    })


control_box = ControlBox()


def web_server():
  html = """<html>
    <head>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <style>
        body{font-family:Arial; text-align: center; margin: 0px auto; padding-top:30px;}
        .switch{position:relative;display:block;width:120px;height:68px;margin-bottom:10px}.switch input{display:none}
        .slider{position:absolute;top:0;left:0;right:0;bottom:0;background-color:#ccc;border-radius:34px}
        .slider:before{position:absolute;content:"";height:52px;width:52px;left:8px;bottom:8px;background-color:#fff;-webkit-transition:.4s;transition:.4s;border-radius:68px}
        input:checked+.slider{background-color:#2196F3}
        input:checked+.slider:before{-webkit-transform:translateX(52px);-ms-transform:translateX(52px);transform:translateX(52px)}
        #control_box{margin:auto; width:10%;}
        #control_box .label{position:relative; right:100%; top:40%}
      </style>
      <script>
        function toggleCheckbox(element) {
          var xhr = new XMLHttpRequest();
          if(element.checked) {
            xhr.open("GET", "/?relay=on", true);
          }
          else {
            xhr.open("GET", "/?relay=off", true);
          }
          xhr.send();
        }

        function controlAntennaRotation(element) {
          var xhr = new XMLHttpRequest();
          var command = element.value;
          console.log("rotation %%o", command);
          xhr.open("POST", "/" + command, true);
          xhr.send();
        }
      </script>
    </head>
    <body>
      <h1>Sancudo IoT Relay Control</h1>
      <form id="control_box" action="#">
        <label class="switch">
          <span class="label">Off</span>
          <input type="radio" id="stop_antenna_rotation" name="direction" value="stop_antenna_rotation" onchange="controlAntennaRotation(this)"><span class="slider"></span>
        </label>
        <label class="switch">
          <span class="label">Clockwise</span>
          <input type="radio" id="rotate_antenna_clockwise" name="direction" value="rotate_antenna_clockwise" onchange="controlAntennaRotation(this)"><span class="slider"></span>
        </label>
        <label class="switch">
          <span class="label">Counter Clockwise</span>
          <input type="radio" id="rotate_antenna_counter_clockwise" name="direction" value="rotate_antenna_counter_clockwise" onchange="controlAntennaRotation(this)"><span class="slider"></span>
        </label>
      </form>
    </body>
  </html>"""
  return html

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
  try:
    conn, addr = s.accept()
    conn.settimeout(3.0)
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    conn.settimeout(None)
    request = str(request)
    print('Content = %s' % request)

    command_match = re.search("POST \/(\w*)", request)
    if command_match is not None:
      command = command_match.group(1)
      print(f"command: {command}")
      getattr(control_box, command)()

    response = web_server()
    conn.send(b'HTTP/1.1 200 OK\n')
    conn.send(b'Content-Type: text/html\n')
    conn.send(b'Connection: close\n\n')
    conn.sendall(response.encode())
    conn.close()
  except OSError as e:
    conn.close()
    print('Connection closed')