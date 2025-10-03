#Configuración Inicial
import random

def jugar_ahorcado():
    nletras=int(input("número de letras (mayor o igual a 3 y menor o igual a 10): "))
    intentos=int(input("número de intentos: "))

    palabras = ["Pikachu", "Bulbasaur", "Charmander", "Squirtle", "Jigglypuff", "Eve", 
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
        return  # Termina esta partida si no hay palabras válidas

    #Desarrollo
    intentos_restantes=intentos
    while intentos_restantes > 0:
        letra = input("ingrese una letra o la palabra completa: ").lower()

        if letra == palabra_azar:
            print("¡Felicidades! Has adivinado la palabra:", palabra_azar)
            break  # Victoria instantánea
        elif len(letra) == 1 and letra in palabra_azar:
            for i in range(nletras):
                if letra == palabra_azar[i]:
                    guiones = guiones[:i] + letra + guiones[i+1:]
            print(guiones)

            if guiones == palabra_azar:
                print("¡Felicidades! Has adivinado la palabra:", palabra_azar)
                break  # Victoria por completar
        else:
            intentos_restantes -= 1
            print("quedan", intentos_restantes, "intentos")

            if intentos_restantes == 0:
                print("¡Has perdido! La palabra era:", palabra_azar)

# Bucle para jugar de nuevo
while True:
    jugar_ahorcado()
    jugar_nuevo = input("¿Quieres jugar de nuevo? (s/n): ").strip().lower()
    if jugar_nuevo != "s":
        print("Gracias por jugar. ¡Hasta la próxima!")
        break
