from globales import *
import copy
import json
import os
import signal
import sys

sys.path.insert(1, "./code")
import salida
import operadores
import norm
import init
import flags
import fitness
import fin
import cromosoma
import compilacion

# Archivo con variables globales


def signal_handler(sig, frame):
    time.sleep(0.5)
    comparar = input("\n ¿Comparar antes de salir?[y/n]: ")
    if comparar == "y" and Gen > 1:

        try:
            salida.archivosEstadisticas(
                historico, directorioBase, Ram, Tiempo, Peso, Rob, Cpu
            )
            fin.salidaFin(
                historico,
                directorioBase,
                Gen,
                Limite,
                tiempo_ini,
                programa,
                dependencias,
                flagsDependencias,
            )
        except:
            print("\n\033[0;0m\033[1;31m [!]Saliendo, error al comparar...")
            os._exit(1)
    elif comparar == "y":
        print(
            "\n\033[0;0m\033[1;31m [!]No se puede comparar con tan pocas generaciones."
        )

    print("\n\033[0;0m\033[1;31m [!]Saliendo...")
    os._exit(1)


signal.signal(signal.SIGINT, signal_handler)

os.system("clear")
print("\033[1;36m", end="")
print("╔" + "═" * 66 + "╗")
print(" " * 10 + "Algoritmo Genético v2 para optimizar programas C" + " " * 10)
print("╚" + "═" * 66 + "╝" + "\n")
print(
    "\033[2m Puedes cambiar la configuración desde el archivo \033[3mconf.ini\033[0m\033[1;36m\033[2m. También"
)
print(
    "\033[2m puedes personalizar las flags en el archivo \033[3mflags.json"
    + "\033[0m\033[2m\033[1;36m o indicando"
)
print(" un nuevo archivo. El resultado de la optimización puede acabar en")
print(" un programa poco estable al tratarse de un proceso de optimización.")
print(
    " Encontrarás diferentes estadisticas de la optimización en el direc-\n torio base configurado.\n"
)


print("\033[0;32m" + " " + "-" * 66 + "\n\n [*]Inicializando flags como objetos")
try:
    with open(path) as file:
        flags = init.inicializacionFlags(file)
except:
    print(
        "\n\n\033[0;0m\033[1;31m [!]El archivo no se pudo abrir, ¿está bien configurado en el archivo de configuración?"
    )
    os._exit(1)

print(" [+]Creando población inicial")
poblacionInicial = init.generarPoblacionAleatoria(tamaño_inicial, flags)
# Poblacion actual
poblacion = poblacionInicial

# Bucle donde se compila, testea, selecciona y se genera la siguiente generación,
# comprobando que no se cumplan los limites impuestos en conf.ini
while True:
    print(" [*]Compilando Generación " + str(Gen))
    directorioGeneracionActual = compilacion.compilarIndividuos(
        directorioBase, Gen, poblacion, programa, dependencias, flagsDependencias, debug
    )
    # Obtener puntuación de cada objetivo y actualizar objeto con puntuación
    print(" [+]Ejecutando pruebas Generación " + str(Gen))
    fitness.test(poblacion, maximoNumeroHilos, directorioGeneracionActual)
    # Normalizar resultados entre 0 y 1
    if Ram:
        print(" [*]Normalizando Ram Generación " + str(Gen))
        norm.normRam(poblacion)
    if Tiempo:
        print(" [*]Normalizando Tiempo Generación " + str(Gen))
        norm.normTiempo(poblacion)
    if Peso:
        print(" [*]Normalizando Peso Generación " + str(Gen))
        norm.normPeso(poblacion)
    if Rob:
        print(" [*]Normalizando Robustez Generación " + str(Gen))
        norm.normRob(poblacion)
    if Cpu:
        print(" [*]Normalizando carga de la CPU Generación " + str(Gen))
        norm.normCpu(poblacion)
    print(" [+]Obteniendo WSM Generación " + str(Gen))
    # Ponderar los resultados según el peso
    norm.wsm(poblacion, Ram, Tiempo, Peso, Rob, Cpu)
    # Seleccionar
    print(" [*]Seleccionando individuos Generación " + str(Gen))
    selected = operadores.selection(copy.deepcopy(poblacion), Select)
    # Fin generacion actual
    historico.append(copy.deepcopy(poblacion))
    if args.imprimir:
        salida.imprimir(poblacion)
    # Comprobar limites para seguir o no
    print(" [+]Comprobando Límites")
    final = operadores.limites(
        Limite, Max_Gen, Gen, Max_Tiempo, tiempo_ini, historico, Generacion_convergencia
    )
    if final:
        print(" [!]Saliendo... ")
        salida.archivosEstadisticas(
            historico, directorioBase, Ram, Tiempo, Peso, Rob, Cpu
        )
        fin.salidaFin(
            historico,
            directorioBase,
            Gen,
            Limite,
            tiempo_ini,
            programa,
            dependencias,
            flagsDependencias,
        )
        sys.exit(0)
    # Preparaciones proxima generación
    Gen += 1
    # Crear nueva Poblacion
    print(" [*]Creando Generación " + str(Gen))
    poblacion = cromosoma.siguienteGeneracion(
        selected, tamaño_general, aleatorios, radiacion, flags
    )
