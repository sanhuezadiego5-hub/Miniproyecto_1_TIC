#Configuración Inicial
import random
from gpiozero import RGBLED, PWMLED, Button, Buzzer
import time

# --- LEDs ---
# LED RGB en pines: R=23, G=27, B=17  (mantengo lo que tú pusiste)
# (Si fuera común ánodo: active_high=False y ánodo a 3V3)
rgb = RGBLED(23, 27, 17, pwm=True, active_high=True)

# LED que se atenúa con las vidas (tú usaste 25)
bar = PWMLED(25)

# --- Buzzer (GPIO12) ---
buzzer = Buzzer(18)

def beep(pattern):
    for on, off in pattern:
        buzzer.on();  time.sleep(on)
        buzzer.off(); time.sleep(off)

# Sonidos (bien diferenciados)
PAT_OK      = [(0.06, 0.04)]  # acierto
PAT_ERROR   = [(0.10, 0.05)]  # error
PAT_VICTORY = [(0.08, 0.05), (0.12, 0.05), (0.16, 0.05), (0.20, 0.10)]  # ascendente
PAT_LOSE    = [(0.25, 0.08), (0.18, 0.06), (0.10, 0.05)]                # descendente

def actualizar_leds(intentos_restantes, intentos_totales):
    frac = intentos_restantes / intentos_totales

    # LED RGB cambia de color según la fracción de vidas
    if frac > 2/3:
        rgb.color = (0,1,0)  # Verde
    elif frac > 1/3:
        rgb.color = (1,0.94,0)  # Amarillo
    else:
        rgb.color = (1,0,0)  # Rojo

    # LED rojo se atenúa proporcionalmente a las vidas
    bar.value = frac

# ======================= MODO BOTONES =======================
# Mapeo que indicaste: azul, negro, rojo, blanco, amarillo
BTN_PINS = {
    "azul": 19,     # +1
    "negro": 26,    # -1
    "rojo": 16,     # +5
    "blanco": 20,   # -5
    "amarillo": 21  # seleccionar
}

ALFA = "abcdefghijklmnopqrstuvwxyz"

def jugar_ahorcado():
    # Pedimos nletras e intentos igual que tu juego original
    nletras=int(input("número de letras (mayor o igual a 3 y menor o igual a 10): "))
    intentos=int(input("número de intentos: "))

    palabras = ["Pikachu", "Bulbasaur", "Charmander", "Squirtle", "Jigglypuff", "Eevee",
        "Snorlax", "Mewtwo", "Mew", "Charizard", "Blastoise", "Venusaur",
        "Raichu", "Gengar", "Alakazam", "Machamp", "Onix", "Lugia","Tyranitar", "Salamence", "Rayquaza", "Zubat", "Pidgey", "Magikarp",
        "Gyarados", "Growlithe", "Arcanine", "Vaporeon", "Jolteon", "Flareon",
        "Espeon", "Umbreon", "Leafeon", "Glaceon", "Sylveon", "Gumshoos", "Grubbin",
        "Trubbish", "Zorua", "Zoroark", "Lucario", "Shinx", "Luxray", "Rotom",
        "Piplup", "Empoleon", "Chimchar", "Infernape", "Turtwig", "Torterra",
        "Deoxys", "Giratina", "Dialga", "Palkia"]

    palabras = [p.lower() for p in palabras]
   
    palabras_filtradas = [p for p in palabras if len(p)==nletras]
    guiones= nletras*"_"
    if palabras_filtradas:
        palabra_azar=random.choice(palabras_filtradas)
        print(guiones)
    else:
        print("no hay palabras con", nletras,"letras en la lista")
        return

    # --- Estado de juego ---
    intentos_restantes=intentos
    actualizar_leds(intentos_restantes, intentos)  # Estado inicial

    # --- Estado de navegación por botones ---
    idx = 0                       # índice en ALFA
    usada = set()                 # letras usadas
    seleccion = {"ready": False, "letra": None}

    # --- Botones (pull-up interno) ---
    b_azul     = Button(BTN_PINS["azul"], pull_up=True, bounce_time=0.05)     # +1
    b_negro    = Button(BTN_PINS["negro"], pull_up=True, bounce_time=0.05)    # -1
    b_rojo     = Button(BTN_PINS["rojo"], pull_up=True, bounce_time=0.05)     # +5
    b_blanco   = Button(BTN_PINS["blanco"], pull_up=True, bounce_time=0.05)   # -5
    b_amarillo = Button(BTN_PINS["amarillo"], pull_up=True, bounce_time=0.05) # seleccionar

    def mostrar_estado():
        print(f"\rPalabra: {guiones}   Letra:[{ALFA[idx]}]   Intentos:{intentos_restantes}   Usadas:{','.join(sorted(usada))}   ",
              end='', flush=True)

    def mover(delta):
        nonlocal idx
        idx = (idx + delta) % len(ALFA)
        mostrar_estado()

    def seleccionar():
        # marca para que el bucle principal lea la "entrada"
        if not seleccion["ready"]:
            seleccion["letra"] = ALFA[idx]
            seleccion["ready"] = True

    # Bind handlers
    b_azul.when_pressed     = lambda: mover(+1)
    b_negro.when_pressed    = lambda: mover(-1)
    b_rojo.when_pressed     = lambda: mover(+5)
    b_blanco.when_pressed   = lambda: mover(-5)
    b_amarillo.when_pressed = seleccionar

    print("\n=== MODO BOTONES ===")
    print("Azul:+1 | Negro:-1 | Rojo:+5 | Blanco:-5 | Amarillo:Seleccionar")
    mostrar_estado()

    # --------- Bucle de juego (igual que el tuyo, pero espera 'seleccionar') ----------
    while intentos_restantes > 0:
        # Espera a que se pulse 'seleccionar' (botón amarillo)
        while not seleccion["ready"]:
            time.sleep(0.02)

        letra = seleccion["letra"]
        seleccion["ready"] = False  # resetea para la próxima selección

        # ----- Lógica original (idéntica salvo que 'letra' viene del botón) -----
        if letra == palabra_azar:
            print("\n¡Felicidades! Has adivinado la palabra:", palabra_azar)
            beep(PAT_VICTORY)
            break
        elif len(letra) == 1 and letra in palabra_azar and letra not in usada:
            usada.add(letra)
            # destapar coincidencias
            nuevo = list(guiones)
            for i in range(nletras):
                if letra == palabra_azar[i]:
                    nuevo[i] = letra
            guiones = "".join(nuevo)
            print("\n" + guiones)
        

            if guiones == palabra_azar:
                print("¡Felicidades! Has adivinado la palabra:", palabra_azar)
                beep(PAT_VICTORY)
                break
        else:
            # fallo (letra no está o se repitió)
            intentos_restantes -= 1
            actualizar_leds(intentos_restantes, intentos)  # Actualizo LEDs
            beep(PAT_ERROR)
            print("\nquedan", intentos_restantes, "intentos")

            if intentos_restantes == 0:
                print("¡Has perdido! La palabra era:", palabra_azar)
                rgb.color = (1,0,0)  # rojo fijo al perder
                bar.value = 0
                beep(PAT_LOSE)

        mostrar_estado()

    # Cierre ordenado de botones (opcional)
    for b in (b_azul, b_negro, b_rojo, b_blanco, b_amarillo):
        b.close()

# Bucle para jugar de nuevo (igual)
while True:
    jugar_ahorcado()
    jugar_nuevo = input("\n¿Quieres jugar de nuevo? (s/n): ").strip().lower()
    if jugar_nuevo != "s":
        print("Gracias por jugar. ¡Hasta la próxima!")
        rgb.off()
        bar.off()
        buzzer.off()
        break
