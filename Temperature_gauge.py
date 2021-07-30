from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import network, time, urequests
from dht import DHT11
from utime import sleep
import framebuf

#declara variables para red
nombre_red = 'FLIAJACOBO_2G' #SSID
contra_red = 'Isabela2014'   #PASSWORD DE SSID

#asigna puertos a sensor dth11 y led rojo
sensorDHT = DHT11 (Pin(15))
cero = Pin(32, Pin.OUT)

#configuracion de pantalla oled
ancho = 128
alto = 64
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = SSD1306_I2C(ancho, alto, i2c)
print(i2c.scan())

#buscar icono
def buscar_icono(ruta):
    dibujo= open(ruta, "rb")  # Abrir en modo lectura de bist
    dibujo.readline() # metodo para ubicarse en la primera linea de los bist
    xy = dibujo.readline() # ubicarnos en la segunda linea
    x = int(xy.split()[0])  # split  devuelve una lista de los elementos de la variable solo 2 elemetos
    y = int(xy.split()[1])
    icono = bytearray(dibujo.read())  # guardar en matriz de bites
    dibujo.close()
    return framebuf.FrameBuffer(icono, x, y, framebuf.MONO_HLSB)

oled.fill(0)  #limpiar
oled.blit(buscar_icono("/arbol.pbm"), 30, 0) # ruta y sitio de ubicación
oled.show()  #mostrar
time.sleep(2)
oled.fill(0)  #limpiar
oled.text('Bienvenido',0,8)
oled.text('Temperature',0,20)
oled.text('Gauge:',0,30)
oled.text('AREANDINA',0,40)
oled.show()

#conectar a wifi
def conectaWifi(red, password):
      global miRed
      miRed = network.WLAN(network.STA_IF)
      miRed.active(True)
      if not miRed.isconnected():              #Si no está conectado…
          miRed.active(True)                   #activa la interface
          miRed.connect(nombre_red, contra_red)         #Intenta conectar con la red
          print('Conectando a la red', nombre_red +"…")
          timeout = time.time()
          while not miRed.isconnected():           #Mientras no se conecte..
              if (time.ticks_diff (time.time (), timeout) > 10):
                  return False
      return True
    
if conectaWifi("nombre_red", "contra_red"):
    print ("Conexión exitosa!")
    print('Datos de la red (IP/netmask/gw/DNS):', miRed.ifconfig())
    #file.flush()
    oled.fill(0)

    #thingspeak
    urll = "https://api.thingspeak.com/update?api_key=7G14OLMNTA3EPJLM"
    #ifttt
    url = "https://maker.ifttt.com/trigger/Error_temperatura/with/key/g5ot3jYEdLifnmrfKO3Ej_Bt0Td0Bh2GpDLq1Vxhpqk?"
    while (True):
        sleep(1)    
        sensorDHT.measure()
        temp =  sensorDHT.temperature()
        hum  =  sensorDHT.humidity()
        print ("T={:02d} ºC, H={:02d} %".format (temp,hum))
        respuesta_thing = urequests.get(urll+"&field1="+str(temp)+"&field2="+str(hum))
        print (respuesta_thing.status_code)
        respuesta_thing.close ()
        #file.flush()
        oled.fill(0)
        oled.text("Temperatura:",0,8)
        oled.text(str(temp),100,8)
        oled.text("Humedad:",0,20)                
        oled.text(str(hum),100,20)
        #oled.text("Kelvin:",0,30)                
        #oled.text(str(kelvin),100,30) 
        oled.show()
        
        if temp > 20 or temp < 10:
            respuesta_iftt = urequests.get(url+"&value1="+str(temp)+"&value2="+str(hum))
            cero.value(1)
            sleep(0.01)
            #print(respuesta.text)
            print (respuesta_iftt.status_code)
            respuesta_iftt.close ()
        
        else:
            cero.value(0)

            
else:
    print('Imposible conectar')
    miRed.active(False)

