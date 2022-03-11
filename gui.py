import tkinter as tk
from tkinter import ttk

class MainGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.DEFAULT_CHARGE_VOLTAGE=14
        self.DEFAULT_DUTY_CYCLE=10
        self.DEFAULT_SYNC_DELAY=0      
        self.DEFAULT_TRIGG_DELAY=1        
        self.DEFAULT_CHARGE_TIMEOUT=200                
        
        self.SCALE=1000/14.5
        
        self.title("Rapid Capacitor Charger")
        self.geometry("365x365+100+100")
        self.bind_all("<Return>", self.enter)  

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

        tk.Label(self.f1,text="Trigg Delay").grid(row=3,column=0, pady=5)
        self.trigg_delay_in=tk.Entry(self.f1,width=8,justify="right")
        self.trigg_delay_in.grid(row=3,column=1,sticky="W")
        tk.Label(self.f1,text="ms").grid(row=3, column=2)

        tk.Label(self.f1,text="Timeout").grid(row=4,column=0, pady=5)
        self.timeout_in=tk.Entry(self.f1,width=8,justify="right")
        self.timeout_in.grid(row=4,column=1,sticky="W")
        tk.Label(self.f1,text="ms").grid(row=4, column=2)

        tk.Button(self.f2,text ="CHARGE!",command=self.charge,height=4, width=15,bg='red').grid(row=0,column=0,pady=10,padx=20)
        tk.Button(self.f2, text="Send Sync", command=self.send_sync).grid(row=1,column=0,pady=10,padx=10)

        tk.Button(self.f3, text="APPLY", command=self.apply).grid(row=11,column=0,padx=15)
        tk.Button(self.f3, text="Default",command=self.default).grid(row=11,column=1,padx=15)
        tk.Button(self.f3, text="Get Info",command=self.getinfo).grid(row=11,column=2,padx=15)
        tk.Button(self.f3, text="Settings",command=self.settings).grid(row=11,column=3,padx=15)

        self.ser_data_text=tk.Text(self.f4,height=7,width=42)
        self.ser_data_text.pack(side=tk.LEFT)
        self.scroll_bar = tk.Scrollbar(self.f4,command=self.ser_data_text.yview)
        self.scroll_bar.pack(side=tk.RIGHT,fill='both')
        self.ser_data_text['yscrollcommand'] = self.scroll_bar.set
        self.ser_data_text.bind('<Button-3>', self.clrser)
             
        self.f1.grid(row=0,column=0) # entry
        self.f2.grid(row=0,column=1) # CHARGE BTN + Send AUX
        self.f3.grid(row=1,column=0,columnspan=2,pady=15) # button row                
        self.f4.grid(row=2,column=0,pady=20,padx=5,columnspan=2) # ser mon
   
    def enter(self,f):
        self.apply()

    def clrser(self,f):
        self.ser_data_text.delete("1.0","end")        

    def default(self):
        self.charge_voltage=self.DEFAULT_CHARGE_VOLTAGE                
        self.duty_cycle=self.DEFAULT_DUTY_CYCLE
        self.sync_delay=self.DEFAULT_SYNC_DELAY
        self.trigg_delay=self.DEFAULT_TRIGG_DELAY
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
            self.trigg_delay_in.delete(0,tk.END)
            self.trigg_delay_in.insert(0,str(self.trigg_delay))
            self.timeout_in.delete(0,tk.END)
            self.timeout_in.insert(0,str(self.charge_timeout))
        except:
            return
    
    def apply(self):
        try:
            self.duty_cycle=int(self.duty_cycle_in.get())
            self.charge_voltage=float(self.charge_voltage_in.get())
            self.fcharge=float(self.charge_voltage)*self.SCALE
            self.dtus=1e6/self.fcharge
            self.sync_delay=int(self.sync_delay_in.get())
            self.charge_timeout=int(self.timeout_in.get())
            self.trigg_delay=int(self.trigg_delay_in.get())
        except:
            return
        
        pwon="marx.PWM_ON_TICS=" + str(10*self.duty_cycle) + "\n"
        pwoff="marx.PWM_OFF_TICS=" + str(1000-10*self.duty_cycle)  + "\n"
        hv="marx.SETPOINT_HV_DT_US=" + str(int(self.dtus))  + "\n"        
        sd="marx.SYNC_DELAY=" + str(self.sync_delay)  + "\n"
        to="marx.CHARGE_TIMEOUT_MS=" + str(self.charge_timeout)  + "\n"

        self.ser_data_text.insert(tk.END,pwon)
        self.ser_data_text.insert(tk.END,pwoff)
        self.ser_data_text.insert(tk.END,hv)
        self.ser_data_text.insert(tk.END,sd)
        self.ser_data_text.insert(tk.END,to)       
        self.ser_data_text.see(tk.END)       
        
    def getinfo(self):
        try:
            self.ser_data_text.insert(tk.END,str(self.charge_voltage) + "\n")
            self.ser_data_text.insert(tk.END,str(self.duty_cycle) + "\n")
            self.ser_data_text.insert(tk.END,str(self.sync_delay) + "\n")
            self.ser_data_text.insert(tk.END,str(self.trigg_delay) + "\n")
            self.ser_data_text.insert(tk.END,str(self.charge_timeout) + "\n")
            self.ser_data_text.see(tk.END)
        except:
            return        

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
            self.trigg_delay=int(self.trigg_delay_in.get())
        except:
            return
        self.ser_data_text.insert(tk.END,"marx.charge()\n")
        self.ser_data_text.see(tk.END)
        
    def send_sync(self):
        self.ser_data_text.insert(tk.END,"marx.send_sync()\n")
        self.ser_data_text.see(tk.END)        

gui=MainGUI()
gui.mainloop()
