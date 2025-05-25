
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import threading
import pygame

class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Temporizador de Testimonios - Emaús")
        self.root.geometry("800x720")  # Aumentar tamaño general
        self.root.configure(bg="#f5f0e1")

        pygame.mixer.init()

        # Estilos ampliados
        style = ttk.Style()
        style.configure("TLabel", background="#f5f0e1", font=("Georgia", 16))
        style.configure("TButton", font=("Georgia", 14))
        style.configure("Timer.TLabel", font=("Georgia", 32, "bold"), background="#ffffff", foreground="#333")
        style.configure("Traffic.TLabel", font=("Helvetica", 48), background="#f5f0e1")

        # Reloj en marco
        reloj_frame = tk.Frame(root, bg="#dcd6cc", bd=2, relief="groove")
        reloj_frame.pack(pady=10, fill="x", padx=30)

        self.clock_label = tk.Label(reloj_frame, font=("Georgia", 28), bg="#dcd6cc", fg="#2d2d2d")
        self.clock_label.pack(pady=(10, 0))
        self.date_label = tk.Label(reloj_frame, font=("Georgia", 18), bg="#dcd6cc", fg="#5a5a5a")
        self.date_label.pack(pady=(0, 10))
        self.update_clock()

        self.create_time_picker("Hora de Inicio", is_start=True)
        self.create_time_picker("Hora de Finalización", is_start=False)

        self.timer_label = ttk.Label(root, text="Temporizador: --:--", style="Timer.TLabel", anchor="center")
        self.timer_label.pack(pady=30)

        self.traffic_light = ttk.Label(root, text="", style="Traffic.TLabel", anchor="center")
        self.traffic_light.pack(pady=20)

        button_frame = tk.Frame(root, bg="#f5f0e1")
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Iniciar", command=self.start_timer).pack(side=tk.LEFT, padx=20)
        ttk.Button(button_frame, text="Reiniciar", command=self.reset_timer).pack(side=tk.LEFT, padx=20)

        self.sound_triggered = {"green": False, "yellow": False, "red": False}

    def create_time_picker(self, label, is_start):
        container = tk.LabelFrame(self.root, text=label, bg="#eae7dc", fg="#2f2f2f", font=("Georgia", 16, "bold"))
        container.pack(padx=30, pady=15, fill="x")

        frame = tk.Frame(container, bg="#eae7dc")
        frame.pack(pady=10)

        hour = ttk.Combobox(frame, width=3, font=("Georgia", 16), values=[f"{i:02}" for i in range(1, 13)])
        minute = ttk.Combobox(frame, width=3, font=("Georgia", 16), values=[f"{i:02}" for i in range(0, 60)])
        ampm = ttk.Combobox(frame, width=4, font=("Georgia", 16), values=["AM", "PM"])
        hour.pack(side=tk.LEFT, padx=4)
        minute.pack(side=tk.LEFT, padx=4)
        ampm.pack(side=tk.LEFT, padx=4)

        if is_start:
            self.start_hour, self.start_minute, self.start_ampm = hour, minute, ampm
            tk.Button(frame, text="Ahora", font=("Georgia", 14), command=self.set_now_start, bg="#b0a990").pack(side=tk.LEFT, padx=8)
        else:
            self.end_hour, self.end_minute, self.end_ampm = hour, minute, ampm
            btn_frame = tk.Frame(container, bg="#eae7dc")
            btn_frame.pack()
            for mins in [20, 30, 40]:
                tk.Button(btn_frame, text=f"+{mins} min", font=("Georgia", 14),
                          command=lambda m=mins: self.add_minutes_to_end(m), bg="#b0a990").pack(side=tk.LEFT, padx=8)

    def update_clock(self):
        now = datetime.now()
        self.clock_label.config(text=now.strftime("%I:%M:%S %p"))
        self.date_label.config(text=now.strftime("%A %d %B %Y"))
        self.root.after(1000, self.update_clock)

    def set_now_start(self):
        now = datetime.now()
        self.start_hour.set(now.strftime("%I"))
        self.start_minute.set(now.strftime("%M"))
        self.start_ampm.set(now.strftime("%p"))

    def add_minutes_to_end(self, minutes_to_add):
        now = datetime.now() + timedelta(minutes=minutes_to_add)
        self.end_hour.set(now.strftime("%I"))
        self.end_minute.set(now.strftime("%M"))
        self.end_ampm.set(now.strftime("%p"))

    def get_time(self, hour_box, minute_box, ampm_box):
        hour = int(hour_box.get())
        minute = int(minute_box.get())
        ampm = ampm_box.get()
        if ampm == "PM" and hour != 12:
            hour += 12
        elif ampm == "AM" and hour == 12:
            hour = 0
        now = datetime.now()
        return now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    def start_timer(self):
        try:
            start_time = self.get_time(self.start_hour, self.start_minute, self.start_ampm)
            end_time = self.get_time(self.end_hour, self.end_minute, self.end_ampm)
            self.remaining_time = (end_time - datetime.now()).total_seconds()
            self.sound_triggered = {"green": False, "yellow": False, "red": False}
            if self.remaining_time > 0:
                self.update_timer()
        except Exception:
            self.timer_label.config(text="Error en la hora")

    def reproducir_sonido(self, archivo):
        def play():
            pygame.mixer.music.load(archivo)
            pygame.mixer.music.play()
        threading.Thread(target=play, daemon=True).start()

    def update_timer(self):
        if self.remaining_time >= 0:
            minutes, seconds = divmod(int(self.remaining_time), 60)
            self.timer_label.config(text=f"Faltan: {minutes:02}:{seconds:02}")

            if minutes < 6:
                self.traffic_light.config(text="🔴", foreground="red")
                if not self.sound_triggered["red"]:
                    self.reproducir_sonido("sounds/middle.mp3")
                    self.sound_triggered["red"] = True
            elif minutes < 11:
                self.traffic_light.config(text="🟡", foreground="orange")
                if not self.sound_triggered["yellow"]:
                    self.reproducir_sonido("sounds/middle.mp3")
                    self.sound_triggered["yellow"] = True
            elif minutes < 16:
                self.traffic_light.config(text="🟢", foreground="green")
                if not self.sound_triggered["green"]:
                    self.reproducir_sonido("sounds/middle.mp3")
                    self.sound_triggered["green"] = True
            else:
                self.traffic_light.config(text="", foreground="black")

            self.remaining_time -= 1
            self.root.after(1000, self.update_timer)
        else:
            self.timer_label.config(text="Tiempo finalizado")
            self.traffic_light.config(text="🔴", foreground="red")
            self.reproducir_sonido("sounds/final.mp3")

    def reset_timer(self):
        self.timer_label.config(text="Temporizador: --:--")
        self.traffic_light.config(text="", foreground="black")
        self.remaining_time = 0
        self.sound_triggered = {"green": False, "yellow": False, "red": False}

if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()
