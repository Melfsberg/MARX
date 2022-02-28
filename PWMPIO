import machine
import time
import rp2

@rp2.asm_pio(set_init=(rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW))
# pin0 - pwm signal, pin1 växlar låg och hög vid varannan pwm puls
# y - första 16 bitar som sänds - pwm tid hög i klockcykler
# x - nästa  16 bitar som sänds - pwm tid låg i klockcykler
def marxpwm():    
    wrap_target()    
    mov(x,isr)         # (1) sparar isr -> x för att använda om ingen ny indata
    pull(noblock)      # (2) pull noblock.. ny data till osr, ingen ny indata x ->  osr
    mov(isr, osr)      # (3) hämtar osr (ny eller gammal data) till isr
    mov(osr,isr)       # (4) hämtar isr till osr
    out(y, 16)         # (5) osr första 16 bitar till y
    out(x, 16)         # (6) osr restrerande 16 bitar till x
    jmp(not_x,"end")   # (7) om indata x är noll, hoppa till end
    set(pins,0b01)     # (8) sätt pin 0 hög (pwm)
    label("on1")
    jmp(y_dec,"on1")   # (9+y) räkna ner till y=0                 
    set(pins,0b00)     # (10+y)sätt pin 0 låg (pwm)
    label("off1")
    jmp(x_dec,"off1")  # (11+x+y) räkna ner till x=0
    nop()        [4]   # (12+x+y) 4 nop för att matcha 1a halvan
    mov(osr,isr)       # (13+x+y) hämtar isr till osr
    out(y, 16)         # (14+x+y) osr första 16 bitar till y
    out(x, 16)         # (15+x+y) osr restrerande 16 bitar till x
    set(pins,0b11)     # (16+x+y) sätt pin 0 och 1 hög (pwm+select b)
    label("on2")
    jmp(y_dec,"on2")   # (17+x+y+y) räkna ner till y=0                
    set(pins,0b00)     # (18+x+y+y) sätt pin 0 och 1 låg (pwm+select b)
    label("off2")
    jmp(x_dec,"off2")  # (19+x+x+y+y) räkna ner till y=1
    wrap()             # börja om
    label("end")
    nop                # gör ingenting om noll har skickats
    jmp("end")         


class PWMMARX:
    # initierar med statemachine nummer (oftast 0), base pin för utsignaler och arbetsfrekvens
    # pin0 - pwm signal, pin1 växlar låg och hög vid varannan pwm puls
    
    def __init__(self, sm_id, pin, count_freq):
        self._sm = rp2.StateMachine(sm_id, marxpwm, freq=count_freq, set_base=machine.Pin(pin))
    
    def start(self):
        # duty behöver sättas innan, annars sätts maskinen i 'stopp'
        self._sm.active(1)

    def reset(self):
        # efter en stop behöver 'maskinen' resettas innan duty och start
        self._sm.active(0)
        self._sm.restart()
    
    def duty(self,duty_off,duty_on):
        # y pwm hög i klockcykler, x pwm låg i klockcykler, max 16 bitars tal (65536)     
        send=duty_off+(duty_on<<16)
        self._sm.put(send)
        
    def stop(self):
        # stoppar pwm omedelbart, för att köra igen behöver duty sättas + maskinen resettas
        self._sm.put(0x00000000)
        

        

pwm=PWMMARX(0,14,20000)

pwm.duty(500,500)

pwm.start()
time.sleep(2)
pwm.stop()
time.sleep(2)
pwm.reset()
pwm.duty(900,100)
pwm.start()
time.sleep(2)
pwm.stop()




    
