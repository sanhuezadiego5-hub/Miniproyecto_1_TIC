import time, random, sys
from gpiozero import LED, Button
import RPi.GPIO as GPIO

# ---------------- Pines (BCM) ----------------
LED_R = 21   # LED rojo
LED_G = 20   # LED verde
LED_B = 16   # LED azul

BTN_R = 26   # Botón rojo
BTN_Y = 19   # Botón amarillo
BTN_B = 13   # Botón azul

LDR_PIN   = 5   # KY-018 fotorresistencia (S)
LASER_PIN = 12  # módulo láser (controlado por GPIO)
BUZZ_PIN  = 6   # buzzer pasivo (PWM)

# -------------- Inicialización GPIO -----------
GPIO.setmode(GPIO.BCM)

# Láser como salida (lo encendemos para apuntar)
GPIO.setup(LASER_PIN, GPIO.OUT)
GPIO.output(LASER_PIN, GPIO.HIGH)  # laser.on()

# LDR como ENTRADA con pull-up interno (tu algoritmo)
GPIO.setup(LDR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Buzzer pasivo por PWM
GPIO.setup(BUZZ_PIN, GPIO.OUT)
_pwm = GPIO.PWM(BUZZ_PIN, 1)
_pwm_started = False

# -------------- Actuadores (gpiozero) --------
led_r = LED(LED_R)
led_g = LED(LED_G)
led_b = LED(LED_B)

btn_r = Button(BTN_R, pull_up=True, bounce_time=0.05)
btn_y = Button(BTN_Y, pull_up=True, bounce_time=0.05)
btn_b = Button(BTN_B, pull_up=True, bounce_time=0.05)

# Encender LED mientras se presiona su botón
btn_r.when_pressed  = led_r.on
btn_r.when_released = led_r.off
btn_y.when_pressed  = led_g.on
btn_y.when_released = led_g.off
btn_b.when_pressed  = led_b.on
btn_b.when_released = led_b.off

# -------------- Sonidos ----------------------
def tone(freq, dur=0.1, duty=50):
    """Tono en buzzer pasivo."""
    global _pwm_started
    if freq <= 0:
        if _pwm_started:
            _pwm.stop(); _pwm_started = False
        time.sleep(dur); return
    _pwm.ChangeFrequency(freq)
    if not _pwm_started:
        _pwm.start(duty)
        _pwm_started = True
    time.sleep(dur)
    _pwm.stop(); _pwm_started = False

def bip_ok():    tone(1200, 0.08)
def bip_fail():  tone(300,  0.12)

def melody_victory():
    for f,d in [(800,0.12),(1000,0.12),(1200,0.18)]:
        tone(f,d); time.sleep(0.04)

def melody_gameover():
    for f,d in [(400,0.25),(300,0.20)]:
        tone(f,d); time.sleep(0.06)

# -------------- Utilidades -------------------
def pedir_bool(msg):
    while True:
        s = input(msg + " (s/n): ").strip().lower()
        if s in ("s","n"): return s == "s"

def pedir_tiempo(msg):
    while True:
        try:
            t = float(input(msg + " (segundos): ").strip())
            if t > 0: return t
        except: pass
        print("Ingresa un número positivo.")

def imprimir_tiempo_restante(t_rest):
    sys.stdout.write(f"\rTiempo restante: {t_rest:4.1f} s ")
    sys.stdout.flush()

def leer_boton_una_vez():
    """Espera hasta detectar una pulsación completa (press+release)."""
    while True:
        if btn_r.is_pressed:
            while btn_r.is_pressed: time.sleep(0.005)
            return 1
        if btn_y.is_pressed:
            while btn_y.is_pressed: time.sleep(0.005)
            return 2
        if btn_b.is_pressed:
            while btn_b.is_pressed: time.sleep(0.005)
            return 3
        time.sleep(0.003)

def gen_secuencia(allow_repeat):
    base = [1,2,3]  # 1=rojo, 2=amarillo, 3=azul
    seq = []
    while len(seq) < 3:
        x = random.choice(base)
        if allow_repeat or x not in seq:
            seq.append(x)
    return seq

def nombre_btn(i): return {1:"Rojo", 2:"Amarillo", 3:"Azul"}[i]

# -------------- Arranque con tu algoritmo ----
def esperar_laser_apuntando():
    """
    Usa exactamente tu algoritmo:
    - GPIO5 como entrada con pull-up
    - not GPIO.input(5) => 'Light detected'
    - Inicia el juego cuando el láser está apuntando a la LDR
    """
    print("Apunta el láser a la fotorresistencia (GPIO5). El juego empezará cuando la LDR detecte luz...")
    while True:
        if not GPIO.input(LDR_PIN):
            print("Light detected")
            break
        else:
            print("Light not detected", end='\r')
        time.sleep(0.1)

# -------------- Juego ------------------------
def juego():
    # 1) Configuración inicial
    Ttotal = pedir_tiempo("Tiempo total del juego")
    permitir_rep = pedir_bool("¿Permitir repetición de botón en la secuencia?")
    seq = gen_secuencia(permitir_rep)
    print("Secuencia creada (oculta). [debug]:", [nombre_btn(i) for i in seq])

    # 2) Espera a que el láser apunte a la LDR (tu método)
    esperar_laser_apuntando()
    t0 = time.time()
    progreso = 0
    penal = 0.0

    # 3) Desarrollo
    while True:
        trans = time.time() - t0
        t_rest = max(0.0, Ttotal - trans - penal)
        imprimir_tiempo_restante(t_rest)
        if t_rest <= 0:
            print("\n¡Tiempo agotado!")
            melody_gameover()
            return False

        boton = leer_boton_una_vez()
        esperado = seq[progreso]

        if boton == esperado:
            progreso += 1
            bip_ok()
            print(f"\nCorrecto: {nombre_btn(boton)} (paso {progreso}/3)")
            if progreso == 3:
                print("¡Secuencia completa! ¡Ganaste!")
                melody_victory()
                return True
        else:
            bip_fail()
            progreso = 0
            penal += 1.0
            print(f"\nFallo: {nombre_btn(boton)} no era el esperado. -1.0 s (total desc {penal:.1f}s)")

def main():
    try:
        while True:
            _ = juego()
            s = input("¿Jugar otra vez? (s/n): ").strip().lower()
            if s != "s":
                break
    finally:
        # Apagar/limpiar
        GPIO.output(LASER_PIN, GPIO.LOW)
        led_r.off(); led_g.off(); led_b.off()
        if _pwm_started:
            _pwm.stop()
        GPIO.cleanup()
        print("Fin.")

if __name__ == "__main__":
    main()
