from machine import Pin
import time

pulse= Pin(14, Pin.IN,Pin.PULL_DOWN)
trigg = Pin(15, Pin.IN,Pin.PULL_DOWN)
volt = Pin(0, Pin.OUT)


frek=1


def int_handler_1(pin):
    global frek
    pulse.irq(handler=None)
    frek+=1
    pulse.irq(handler=int_handler_1)
 
def int_handler_2(pin):
    global frek
    trigg.irq(handler=None)
    frek=1
    trigg.irq(handler=int_handler_2) 
 
pulse.irq(trigger=machine.Pin.IRQ_RISING, handler=int_handler_1)
trigg.irq(trigger=machine.Pin.IRQ_RISING, handler=int_handler_2)


while True:
    
    volt.value(1)
    time.sleep_ms(int(100//frek))
    volt.value(0)
    time.sleep_ms(int(900//frek))
