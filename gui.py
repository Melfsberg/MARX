import tkinter as tk
import serial

class MainGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.DEFAULT_CHARGE_VOLTAGE=10
        self.DEFAULT_DUTY_CYCLE=10
        self.DEFAULT_SYNC_DELAY=0      
        self.DEFAULT_CHARGE_TIMEOUT=100                
        
        self.SCALE=1000/14.5
        
        self.title("Rapid Capacitor Charger")
        self.geometry("365x400+100+100")
        self.bind_all("<Return>", self.enter)  

        self.protocol("WM_DELETE_WINDOW", self.exit)

        self.f1=tk.Frame(self.master)
        self.f2=tk.Frame(self.master)
        self.f3=tk.Frame(self.master)
        self.f4=tk.Frame(self.master)
                
        tk.Label(self.f1,text="Charge Voltage").grid(row=0, column=0, pady=5)
        self.charge_voltage_in=tk.Entry(self.f1,width=8,justify="right")
        self.charge_voltage_in.grid(row=0, column=1,sticky="W")
        tk.Label(self.f1,text="kV").grid(row=0, column=2)

        tk.Label(self.f1,text="Duty Cycle").grid(row=1,column=0, pady=5)
        self.duty_cycle_in=tk.Entry(self.f1,width=8,justify="right")
        self.duty_cycle_in.grid(row=1, column=1,sticky="W")
        tk.Label(self.f1,text="%").grid(row=1, column=2)

        tk.Label(self.f1,text="Sync Delay").grid(row=2, column=0, pady=5)
        self.sync_delay_in=tk.Entry(self.f1,width=8,justify="right")
        self.sync_delay_in.grid(row=2, column=1,sticky="W")
        tk.Label(self.f1,text="ms").grid(row=2, column=2)

        tk.Label(self.f1,text="Timeout").grid(row=3,column=0, pady=5)
        self.timeout_in=tk.Entry(self.f1,width=8,justify="right")
        self.timeout_in.grid(row=3,column=1,sticky="W")
        tk.Label(self.f1,text="ms").grid(row=3, column=2)

        tk.Button(self.f2,text ="CHARGE!",command=self.charge,height=4, width=12,bg='red').grid(row=2,column=1,pady=10,padx=30)
        tk.Button(self.f2, text="Send Sync", command=self.send_sync).grid(row=3,column=1,pady=10)

        tk.Button(self.f3, text="Apply", command=self.apply).grid(row=11,column=0,padx=15)
        tk.Button(self.f3, text="Default",command=self.default).grid(row=11,column=1,padx=15)
        tk.Button(self.f3, text="Get Info",command=self.getinfo).grid(row=11,column=2,padx=15)
        # tk.Button(self.f3, text="Settings",command=self.settings).grid(row=11,column=3,padx=15)

        self.ser_data_text=tk.Text(self.f4,height=10,width=42)
        self.ser_data_text.pack(side=tk.LEFT)
        self.scroll_bar = tk.Scrollbar(self.f4,command=self.ser_data_text.yview)
        self.scroll_bar.pack(side=tk.RIGHT,fill='both')
        self.ser_data_text['yscrollcommand'] = self.scroll_bar.set
        self.ser_data_text.bind('<Button-3>', self.clrser)
        self.ser_data_text.bind("<Key>", lambda e: "break")
             
        self.f1.grid(row=0,column=0) # entry
        self.f2.grid(row=0,column=1) # CHARGE BTN + Send AUX
        self.f3.grid(row=1,column=0,columnspan=2,pady=15) # button row                
        self.f4.grid(row=2,column=0,pady=20,padx=5,columnspan=2) # ser mon
   
    def enter(self,*_):
        self.apply()

    def clrser(self,*_):
        self.ser_data_text.delete("1.0","end")        

    def default(self):
        self.charge_voltage=self.DEFAULT_CHARGE_VOLTAGE                
        self.duty_cycle=self.DEFAULT_DUTY_CYCLE
        self.sync_delay=self.DEFAULT_SYNC_DELAY
        self.charge_timeout=self.DEFAULT_CHARGE_TIMEOUT 
                
        self.update()    
        self.apply()
        
    def update(self):
        try:
            self.ser_data_text.delete("1.0","end")
            self.charge_voltage_in.delete(0,tk.END)
            self.charge_voltage_in.insert(0,str(self.charge_voltage))
            self.duty_cycle_in.delete(0,tk.END)
            self.duty_cycle_in.insert(0,str(self.duty_cycle))
            self.sync_delay_in.delete(0,tk.END)
            self.sync_delay_in.insert(0,str(self.sync_delay))
            self.timeout_in.delete(0,tk.END)
            self.timeout_in.insert(0,str(self.charge_timeout))
        except:
            tk.messagebox.showerror("Error!", "Kontakta Mattias!")
            return
    
    def apply(self):
        try:
            self.duty_cycle=int(self.duty_cycle_in.get())
            self.charge_voltage=float(self.charge_voltage_in.get())
            self.fcharge=float(self.charge_voltage)*self.SCALE
            self.dtus=1e6/self.fcharge
            self.sync_delay=int(self.sync_delay_in.get())
            self.charge_timeout=int(self.timeout_in.get())
        except:
            tk.messagebox.showerror("Error!", "Settings not complete!")
            return
        
        pwon="marx.PWM_ON_TICS=" + str(10*self.duty_cycle) + "\r"
        pwoff="marx.PWM_OFF_TICS=" + str(1000-10*self.duty_cycle)  + "\r"
        hv="marx.SETPOINT_HV_DT_US=" + str(int(self.dtus))  + "\r"        
        sd="marx.SYNC_DELAY=" + str(self.sync_delay)  + "\r"
        to="marx.CHARGE_TIMEOUT_MS=" + str(self.charge_timeout)  + "\r"

        self.ser.write("\r".encode())
        self.ser.write(pwon.encode())
        self.ser.write(pwoff.encode())
        self.ser.write(hv.encode())
        self.ser.write(sd.encode())
        self.ser.write(to.encode())
          
    def getinfo(self):
        try:
            self.ser.write("\r".encode())
            self.ser.write("marx.PWM_ON_TICS\r".encode())
            self.ser.write("marx.PWM_OFF_TICS\r".encode())
            self.ser.write("marx.SETPOINT_HV_DT_US\r".encode())  
            self.ser.write("marx.SYNC_DELAY\r".encode()) 
            self.ser.write("marx.CHARGE_TIMEOUT_MS\r".encode())
        except:
            tk.messagebox.showerror("Error!", "No serial device!")

            


    def settings(self):
        pass
    
    def charge(self):        
        try:
            self.duty_cycle=int(self.duty_cycle_in.get())
            self.charge_voltage=float(self.charge_voltage_in.get())
            self.fcharge=float(self.charge_voltage)*self.SCALE
            self.dtus=1e6/self.fcharge
            self.sync_delay=int(self.sync_delay_in.get())
            self.charge_timeout=int(self.timeout_in.get())
        except:
            tk.messagebox.showerror("Error!", "No settings avaible!")
            return
        
        pwon="marx.PWM_ON_TICS=" + str(10*self.duty_cycle) + "\r"
        pwoff="marx.PWM_OFF_TICS=" + str(1000-10*self.duty_cycle)  + "\r"
        hv="marx.SETPOINT_HV_DT_US=" + str(int(self.dtus))  + "\r"        
        sd="marx.SYNC_DELAY=" + str(self.sync_delay)  + "\r"
        to="marx.CHARGE_TIMEOUT_MS=" + str(self.charge_timeout)  + "\r"

        self.ser.write("\r".encode())
        self.ser.write(pwon.encode())
        self.ser.write(pwoff.encode())
        self.ser.write(hv.encode())
        self.ser.write(sd.encode())
        self.ser.write(to.encode())
        self.ser.write("marx.charge()\r".encode())

    def send_sync(self):
        self.ser.write("\r".encode())
        self.ser.write("marx.send_sync()\r".encode())
        
    def init_serial(self):
        #dev="/dev/tty.usbmodem14201"
        dev="COM8"

        self.ser=serial.Serial(dev)
        self.ser.write("\r".encode())
        self.read_ser()

    def read_ser(self):
        if self.ser.in_waiting:
            self.ser_data_text.insert(tk.END,(self.ser.read(self.ser.in_waiting)))
            self.ser_data_text.see(tk.END)
        self._job=self.after(100,self.read_ser)
        
    def exit(self):
        self.after_cancel(self._job)
        self.ser.close()
        self.destroy()      

gui=MainGUI()
gui.init_serial()

gui.mainloop()
