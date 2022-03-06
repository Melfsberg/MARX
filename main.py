import machine
import utime
import rp2

@rp2.asm_pio(set_init=(rp2.PIO.OUT_LOW, rp2.PIO.OUT_LOW))
# pin0 - pwm signal, pin1 växlar låg och hög vid varannan pwm puls
# y - första 16 bitar som sänds - pwm tid hög i klockcykler
# x - nästa  16 bitar som sänds - pwm tid låg i klockcykler
def pwmpio():    
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
    nop()              # (12+x+y) 1 nop för att motsvara mov(x,ist) i första halvan
    nop()              # (13+x+y) 1 nop för att motsvara pull(noblock) i första halvan
    nop()              # (14+x+y) 1 nop för att motsvara mov(isr,osr) i första halvan
    set(pins,0b10)     # (15+x+y) för att motsvara jmp(not_x,"end" i första halvan
    mov(osr,isr)       # (16+x+y) hämtar isr till osr
    out(y, 16)         # (17+x+y) osr första 16 bitar till y
    out(x, 16)         # (18+x+y) osr restrerande 16 bitar till x
    set(pins,0b11)     # (19+x+y) sätt pin 0 och 1 hög (pwm+select b)
    label("on2")
    jmp(y_dec,"on2")   # (20+x+y+y) räkna ner till y=0                
    set(pins,0b00)     # (21+x+y+y) sätt pin 0 och 1 låg (pwm+select b)
    label("off2")
    jmp(x_dec,"off2")  # (22+x+x+y+y) räkna ner till y=1
    wrap()             # börja om
    label("end")
    nop                # gör ingenting om noll har skickats
    jmp("end")         

class RCCharger:
    # initierar med statemachine nummer (oftast 0), base pin för utsignaler och arbetsfrekvens
    # pin0 - pwm signal, pin1 växlar låg och hög vid varannan pwm puls    
    def __init__(self, sm_id, pin, count_freq):
        self._sm = rp2.StateMachine(sm_id, pwmpio, freq=count_freq, set_base=machine.Pin(pin))
        self._timeout=machine.Timer()
        self._hvin = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_DOWN)
        self._trigout = machine.Pin(2,machine.Pin.OUT,value=0)
        self._auxout = machine.Pin(15,machine.Pin.OUT,value=0)
        self._emergencyin = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_DOWN)

        self.hvin_current_dt_us=0
        self._hvin_prev_time_us=0
        
        self.timed_out=False
        self.triggered=False
        self.charging=False
        self.emergency=False

        self.SETPOINT_HV_DT_US=1000
        self.PWM_ON_TICS=100
        self.PWM_OFF_TICS=900
        self.CHARGE_TIMEOUT_MS=200
        self.SYNC_DELAY=0
                
    def start_pwm(self):                 # duty behöver sättas innan, annars sätts maskinen i 'stopp'
        self._sm.active(1)
  
    def stop_pwm(self):                  # stoppar pwm omedelbart, för att köra igen behöver duty sättas + maskinen resettas
        self._sm.put(0x00000000)
        self._hvin.irq(handler=None)
        self._timeout.deinit()
        self.charging=False
        self.timed_out=True

    def reset_pwm(self):                 # efter en stop behöver 'maskinen' resettas innan duty och start        
        self._sm.active(0)
        self._sm.restart()
    
    def set_duty_pwm(self,duty_off,duty_on): # y pwm hög i klockcykler, x pwm låg i klockcykler, max 16 bitars tal (65536)     
        send=duty_off+(duty_on<<16)
        self._sm.put(send)       

    def charge(self):
        self.triggered=False
        self.timed_out=False
        self.emergency=False
        
        if not(self._emergencyin.value()):
            self.emergency=True
            print("emergency shutdown")
            return

        self.charging=True
        self.hvin_current_dt_us=self.SETPOINT_HV_DT_US*128
        self._hvin_prev_time_us=utime.ticks_us()        
        self._timeout.init(mode=machine.Timer.ONE_SHOT,period=self.CHARGE_TIMEOUT_MS,callback=self._timeout_irqhandler)
        self._hvin.irq(trigger= machine.Pin.IRQ_FALLING, handler=self._hvin_irqhandler)

        self.send_sync()
        self.reset_pwm()        
        self.set_duty_pwm(self.PWM_OFF_TICS,self.PWM_ON_TICS)
        self.start_pwm()

        while self.charging:
            pass       
                
    def send_trigg(self):
        utime.sleep_us(1000)       
        print("dt",self.hvin_current_dt_us,"us. f", 1000000/self.hvin_current_dt_us,"Hz")
        self._trigout.value(1)
        utime.sleep_ms(1)
        self._trigout.value(0)
        self.triggered=True
        print("trigged")
        
    def send_sync(self):
        self._auxout.value(1)
        utime.sleep_ms(1)
        self._auxout.value(0)

    def _timeout_irqhandler(self,t):           # avbrottsrutin när uppladdningstimern maxat ut        
        self.stop_pwm()
        self.timed_out=True
        print("timed out")
                                    
    def _hvin_irqhandler(self,pin):            # avbrottsrutin vid puls från uppladdningsspänningspulståget
         self._hvin.irq(handler=None)     
         now=utime.ticks_us()
         self.hvin_current_dt_us=utime.ticks_diff(now,self._hvin_prev_time_us)
         if self.hvin_current_dt_us<=self.SETPOINT_HV_DT_US:
            self.stop_pwm()
            self.send_trigg()
         else:
             self._hvin_prev_time_us=now
             self._hvin.irq(trigger= machine.Pin.IRQ_FALLING, handler=self._hvin_irqhandler)
              
marx=RCCharger(0,0,6_000_000)

