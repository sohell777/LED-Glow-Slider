from machine import Pin, PWM, ADC
import network
import socket

# Setup LED PWM
LED_PIN =0 # Adjust this according to your wiring
led = PWM(Pin(LED_PIN), freq=1000)
led.duty_u16(0)

# Setup LDR sensor
LDR_PIN = 26  # Adjust this according to your wiring
ldr = ADC(Pin(LDR_PIN))

# Connect to Wi-Fi
ssid = 'DE-LAB'
password = None

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

while not station.isconnected():
    pass

print('Connection successful')
print(station.ifconfig())

# HTML Web Page
def web_page():
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lux Intensity Range Input</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #f0f0f0;
            margin: 0;
        }
        .container {
            text-align: center;
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        .lux-value {
            margin-top: 10px;
            font-size: 24px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Lux Intensity Range Input</h1>
        <label for="luxRange">Intensity (lux):</label><br>
        <input type="range" id="luxRange" name="luxRange" min="0" max="65536" value="0" oninput="updateLuxValue(this.value)">
        <div class="lux-value" id="luxValue">0 lux</div>
    </div>
    <script>
        function updateLuxValue(value) {
            document.getElementById('luxValue').textContent = value + ' lux';
            fetch('/set_brightness?intensity=' + value);
        }
    </script>
</body>
</html>"""
    return html

# Handle HTTP Requests
def handle_request(request):
    request = request.decode('utf-8')
    request_line = request.split('\n')[0]
    method, path, _ = request_line.split()
    
    if method == 'GET':
        if path == '/':
            response = web_page()
        elif path.startswith('/set_brightness'):
            query = path.split('?')[1]
            params = {key: value for key, value in (param.split('=') for param in query.split('&'))}
            intensity = int(params.get('intensity', 0))
            
            brightness=intensity
            
            led.duty_u16(brightness)
            response = f'Brightness set to {brightness // 655}'
        else:
            response = '404 Not Found'
    else:
        response = '405 Method Not Allowed'
    
    return response

# Start Web Server
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
server_socket = socket.socket()
server_socket.bind(addr)
server_socket.listen(1)

print('Listening on', addr)

try:
    while True:
        client_socket, client_addr = server_socket.accept()
        print('Client connected from', client_addr)
        request = client_socket.recv(1024)
        response = handle_request(request)
        client_socket.sendall('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n' + response)
        client_socket.close()
except KeyboardInterrupt:
    pass
finally:
    server_socket.close()
