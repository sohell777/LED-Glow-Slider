from machine import Pin, PWM, ADC
import network
import socket

# Setup LED PWM
LED_PIN = 0  # Adjust this according to your wiring
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

# Handle HTTP Requests
def handle_request(request):
    request = request.decode('utf-8')
    request_line = request.split('\n')[0]
    method, path, _ = request_line.split()
    
    if method == 'GET':
        if path.startswith('/set_brightness'):
            query = path.split('?')[1]
            params = {key: value for key, value in (param.split('=') for param in query.split('&'))}
            intensity = int(params.get('intensity', 0))
            brightness = intensity
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
        client_socket.sendall('HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n' + response)
        client_socket.close()
except KeyboardInterrupt:
    pass
finally:
    server_socket.close()
