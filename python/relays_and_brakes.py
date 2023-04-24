try:
  from machine import Pin
except:
  class Pin:
    OUT = "OUT"

    def __init__(self, id_, mode=None):
      print(f"Mocking pin {id_}")
      self._id = id_
      self._value = None

    def value(self, value_to_set=None):
      if value_to_set is not None:
        print(f"Setting pin {self._id} to {value_to_set}")
        self._value = value_to_set
      else:
        return self._value

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
try:
  import usocket as socket
except:
  import socket

relay=Pin(3,Pin.OUT)


def web_server():
  if relay.value() == 1:
    relay_state = ''
  else:
    relay_state = 'checked'
  html = """<html>
    <head>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <style>
        body{font-family:Arial; text-align: center; margin: 0px auto; padding-top:30px;}
        .switch{position:relative;display:inline-block;width:120px;height:68px}.switch input{display:none}
        .slider{position:absolute;top:0;left:0;right:0;bottom:0;background-color:#ccc;border-radius:34px}
        .slider:before{position:absolute;content:"";height:52px;width:52px;left:8px;bottom:8px;background-color:#fff;-webkit-transition:.4s;transition:.4s;border-radius:68px}
        input:checked+.slider{background-color:#2196F3}
        input:checked+.slider:before{-webkit-transform:translateX(52px);-ms-transform:translateX(52px);transform:translateX(52px)}
      </style>
      <script>
        function toggleCheckbox(element) {
          var xhr = new XMLHttpRequest();
          if(element.checked) {
            xhr.open("GET", "/?relay=on", true);
          }
          else {
            xhr.open("GET", "/?relay=off", true); } xhr.send();
          }
      </script>
    </head>
    <body>
      <h1>Sancudo IoT Relay Control</h1>
      <table>
        <tr>
          <td>CCW Relay</td>
          <td>
            <label class="switch">
              <input name="relay" type="checkbox" onchange="toggleCheckbox(this)" %s><span class="slider"></span>
            </label>
          </td>
        </tr>
        <tr>
          <td>CW Relay</td>
          <td>
            <label class="switch">
              <input name="relay" type="checkbox" onchange="toggleCheckbox(this)" %s><span class="slider"></span>
            </label>
          </td>
        </tr>
      </table>
    </body>
  </html>""" % (relay_state, relay_state)
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
    relay_on = request.find('/?relay=on')
    relay_off = request.find('/?relay=off')
    if relay_on == 6:
      print('RELAY ON')
      relay.value(0)
    if relay_off == 6:
      print('RELAY OFF')
      relay.value(1)
    response = web_server()
    conn.send(b'HTTP/1.1 200 OK\n')
    conn.send(b'Content-Type: text/html\n')
    conn.send(b'Connection: close\n\n')
    conn.sendall(response.encode())
    conn.close()
  except OSError as e:
    conn.close()
    print('Connection closed')
