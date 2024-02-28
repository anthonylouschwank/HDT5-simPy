import simpy
import random
import math #Manipulacion de datos para hacer las graficas mas faciles
RANDOM_SEED = 42
Procesos_Nuevos = 150
Procesos_entre_Intervalos = 10
Min_Espera = 1  
Max_Espera = 3
tiempos_finalizacion = [] #Lista donde se guardan los numeros de los tiempos

def source(env, number, interval, procesador): #"Driver del programa"
    for i in range(number):
        instrucciones = random.randint(1, 10)
        p = Proceso(env, 'Proceso%02d' % i, procesador, time_in_processor=3.0, instrucciones=instrucciones)
        env.process(p)
        t = random.expovariate(1.0 / interval)
        yield env.timeout(t)

def Proceso(env, name, procesador, time_in_processor, instrucciones):
    global tiempos_finalizacion
    Llegada = env.now
    print('%7.4f %s: Entrando' % (Llegada, name)) 
    
    with procesador.request() as req:
        waiting = random.uniform(Min_Espera, Max_Espera) #Declaramos cuanto tiempo esperara el proceso antes 
        wait = env.now - Llegada #Decimos cuanto espera
        
        while instrucciones >= 3:  
            results = yield req | env.timeout(waiting) #Si tiene mas de o igual a 3, entra al sistema
            cupo = random.randint(1, 2) #Decide si es su turno o no aleatoriamente
            if cupo == 1:
                print('%7.4f %s: RECHAZADO POR CUPO' % (env.now, name))
                results = yield req | env.timeout(waiting)  #Si le toca uno le toca salir de la lista de espera y volver a intentar
            elif cupo == 2:
                if req in results: #Inicia el proceso de ver tiempos y quitar instrucciones
                    print('%7.4f %s: Espero %6.3f' % (env.now, name, wait))
                    instrucciones -= 3
                    tim = random.expovariate(1.0 / time_in_processor)
                    yield env.timeout(tim)

                    tiempos_finalizacion.append(env.now) #Agregamos a la lista de tiempos
                    
                    print('%7.4f %s: Termine' % (env.now, name)) #Esto indica que todo fue bien y el proceso elimino todas sus instrucciones o tiene menos de 3
                else:
                    print('%7.4f %s: RECHAZADO AFT %6.3f' % (env.now, name, wait)) #Sino no
           
print("Procesador Empieza")
random.seed(RANDOM_SEED)
env = simpy.Environment()

procesador = simpy.Resource(env, capacity=2)
env.process(source(env, Procesos_Nuevos, Procesos_entre_Intervalos, procesador))
env.run()

media = sum(tiempos_finalizacion) / len(tiempos_finalizacion)
print("Media de los tiempos de finalización:", media)

diferencias_cuadradas = [(tiempo - media) ** 2 for tiempo in tiempos_finalizacion]
media_cuadrados_diferencias = sum(diferencias_cuadradas) / len(diferencias_cuadradas)
desviacion_estandar = math.sqrt(media_cuadrados_diferencias)

print("Desviación estándar de los tiempos de finalización:", desviacion_estandar)
