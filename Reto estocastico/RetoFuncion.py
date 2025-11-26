import pandas as pd
import numpy as np

# Parámetros para realizar las pruebas
nClientes= 100
nTiempo= 8
Camiones=1
nRampas=1
VCarro=7.36

numSimulaciones =2


def simulacion():
    #Cargar la matriz de distancias en línea recta
    df= pd.read_excel('distancias_extras.xlsx',index_col='Unnamed: 0')
    df = df.astype(float)

    #Guardar fila 0
    fila0=pd.DataFrame(df.loc[0])
    fila0=fila0.T

    #Borrar fila 0
    df = df.drop(index=0)

    #Escoger una muestra de 100 nodos aleatorios

    # Concatenar la fila de 0 siempre y escoger 100 clientes aleatorios
    dF=df.sample(n=nClientes)
    dF = pd.concat([fila0, dF], ignore_index=False)

    # Dejar solamente las columnas correspondientes a las filas
    nodos=list(dF.index)
    nodoss=[(x) for x in nodos]
    dF=dF[nodoss]

    #Cambiar el nombre de las columnas y filasde 0 a 100
    dF=dF.reset_index(drop=True)
    dF.columns
    new_column_names = {old_name: i for i, old_name in enumerate(dF.columns)}
    dF.rename(columns=new_column_names, inplace=True)

    dict_from_df = dF.to_dict(orient='index')

    #Evitar que el nodo viaje a sí mismo
    for i in dict_from_df.keys():
        dict_from_df[i].pop(i)

    #Cargar matriz de distancias en auto
    dr= pd.read_excel('rutas_auto.xlsx',index_col='Unnamed: 0')
    dr=dr.reset_index(drop=True)
    new_column_names = {old_name: i for i, old_name in enumerate(dr.columns)}
    dr.rename(columns=new_column_names, inplace=True)

    dR=dr.loc[nodos]
    # Dejar solamente las columnas correspondientes a las filas
    nodoS=list(dR.index)
    dR=dR[nodoS]
    #Cambiar el nombre de las columnas y filas de 0 a 100
    dR=dR.reset_index(drop=True)
    dR.columns
    new_column_names = {old_name: i for i, old_name in enumerate(dR.columns)}
    dR.rename(columns=new_column_names, inplace=True)

    dict_from_dr = dR.to_dict(orient='index')

    #Evitar que el nodo viaje a sí mismo
    for i in dict_from_dr.keys():
        dict_from_dr[i].pop(i)
    dict_from_dr

    #Cargar matriz de tiempo en carro
    dt= pd.read_excel('matriz_tiempo.xlsx',index_col='Unnamed: 0')
    dt=dt.reset_index(drop=True)
    new_column_names = {old_name: i for i, old_name in enumerate(dt.columns)}
    dt.rename(columns=new_column_names, inplace=True)

    dT=dt.loc[nodos]
    # Dejar solamente las columnas correspondientes a las filas
    nodoS=list(dT.index)
    dT=dT[nodoS]
    #Cambiar el nombre de las columnas y filas de 0 a 100
    dT=dT.reset_index(drop=True)
    dT.columns
    new_column_names = {old_name: i for i, old_name in enumerate(dT.columns)}
    dT.rename(columns=new_column_names, inplace=True)

    dict_from_dt = dT.to_dict(orient='index')

    #Evitar que el nodo viaje a sí mismo
    for i in dict_from_dt.keys():
        dict_from_dt[i].pop(i)
    dict_from_dt


    #Usar tabla con la descripción de los productos para calcular el volumen de la entrega
    dP= pd.read_csv('info_productos.csv',index_col='Producto')
    dictProductos = dP.to_dict(orient='index')
    #Cargar tabla con 10,000 simulaciones de montecarlo con la distribución de los pedidos de productos
    compras=pd.read_excel("simulacion_final_completa.xlsx",index_col='Cliente')



    # Obtener 100 muestras random
    CC = compras.sample(n=nClientes+1)
    CC = CC.reset_index(drop=True)
    dCompra=CC.to_dict(orient='index')
    dCompra[0]=VCarro

    #Copiar dCompra para tener el estado inicial
    import copy
    E=copy.deepcopy(dCompra)
    clients=list(E.keys())
    clients.remove(0)
    for i in clients:
        E[i]['Unidades']=0

    #Función para determinar el volumen de la compra
    def calcularVolumen(cliente):
            totalV=0
            #Si se regresa a la bodega vaciar el camión y dejarlo disponible para cargar todo el volumen disponible
            if cliente == 0:
                    return -VCarro
                    exit()

                
            cant=dCompra[cliente]['Unidades']
            totalV+=dictProductos[dCompra[cliente]['Producto']][' Volumen mtro3']*cant
                
            return totalV
    
    def tRes(a,state,res):
        if a == 0:
            if res ==0:
                return -(nTiempo-1)
                exit()
        return dict_from_dt[state[-1][0]][a]

    #---------------------------------------------------------------------------------------------------------------
    #    Esqueleto de PSA para el problema VRP
    #---------------------------------------------------------------------------------------------------------------

    from simpleai.search import SearchProblem, depth_first, breadth_first, uniform_cost, greedy, astar
    from simpleai.search.viewers import BaseViewer, ConsoleViewer, WebViewer

    import time
    import copy

    #---------------------------------------------------------------------------------------------------------------
    #   Definición del problema
    #---------------------------------------------------------------------------------------------------------------

    class Tour(SearchProblem):
        """ 
            Clase que es usada para definir el problema de VRP. Los estados son representados 
            con los números de nodos.
        """

        def __init__(self, origen):
            """ Constructor de la clase. Inicializa el problema de acuerdo a ...
        
                origen: No se ha entregado ningún paquete
                destino: Ya se entregaron todos los paquetes y se regresa a la base
            """
            
            #Restricciones
            self.capacidad=VCarro
            self.tiempo=nTiempo-1
            self.idCamion=1
            self.dia=1
            self.rampas=nRampas
            #Pedido entregado 
            pedidos=0
            #Tiempo restante en los camiones
            self.statuscamiones = [nTiempo] * Camiones
            
            #Asignar n las horas dependiendo de la cantidad de rampas
            if self.rampas==2:
                for i in range(0, len(self.statuscamiones), self.rampas):
                    self.statuscamiones[i] = self.statuscamiones[i + 1] = (self.statuscamiones[i]-(i+1))
            
            elif self.rampas==3:
                for i in range(0, len(self.statuscamiones), self.rampas):
                    self.statuscamiones[i] = self.statuscamiones[i + 1] = self.statuscamiones[i + 2]  = (self.statuscamiones[i]-(i+1))
                
            elif self.rampas ==1:
                for i in range(len(self.statuscamiones)):
                    self.statuscamiones[i]-=(i+1)
            
            self.statuscamiones=tuple(self.statuscamiones)

            origen=[(0,0,self.capacidad,self.tiempo,self.statuscamiones,self.idCamion,self.dia)]
            origen=tuple(origen)
            SearchProblem.__init__(self, origen)
            
        
        def actions(self, state):
            """ 
                Este método regresa una lista con las acciones posibles que pueden ser ejecutadas de 
                acuerdo con el estado especificado.
                
                state: Numero del nodo actual
            
            """
            posible = list(dict_from_df[state[-1][0]].keys())
            posible = posible[:nClientes]
            posible = [int(element) for element in posible]
            p=copy.deepcopy(posible)

            #Evitar pasarse del volumen
            listt=[]
            for j in p:
               
                if((state[-1][2]-calcularVolumen(j))<0):
                    listt.append(j)
                   
            for i in listt:
                if i in posible:
                    posible.remove(i)
            
            
            #Evitar pasarse del tiempo
            listt=[]
            for j in p:
                
                
                if(state[-1][0]!=0):
                    if(j!=0):
                        if((state[-1][3]-dict_from_dt[state[-1][0]][j])<=dict_from_dt[j][0]):
                        
                            listt.append(j)
                        
            for i in listt:
                if i in posible:
                    posible.remove(i)

            #Remover los nodos ya visitados
            lista=[]
            for i in state:
                if i[0]!=0:
                    lista.append(i[0])
        
            for i in lista:
                if i in posible:
                    posible.remove(i)
            
        
            
            posible = [int(element) for element in posible]
            
            
            
        
            
            return posible #Regresar lista con el nombre de nodos posibles

            

        def result(self, state, action):
            """ 
                Este método regresa el nuevo estado obtenido despues de ejecutar la acción.

                state: Nodo origen (el actual).
                action: Nodo especificado por action
            """
            
            
            
            #Copiar el estado actual
            s=list(state)
            s=s.copy()
            dia=state[-1][6]
            if(action==0):
                dia+=1
                #print('algoo')
                demand=dCompra[action]
            if(action !=0):
                demand=tuple(dCompra[action].items())
            
            
            #Calcular el volumen del pedido
            volumenTrasladado=s[-1][2]-calcularVolumen(action)
            restriccion=0
            if volumenTrasladado>=VCarro:
                volumenTrasladado=VCarro
                restriccion=1

            

            #Calcular el tiempo que va a tomar hacer la acción
            tiempoRestante=s[-1][3]-(tRes(action,state,restriccion))
            if tiempoRestante>=(nTiempo):
                tiempoRestante=(nTiempo)
                
            #Cambiar el tiempo restante a los camiones
            tiempos=state[-1][4]
            tiempos=list(tiempos)
            
            tiempos[(state[-1][5])-1]=tiempoRestante
            restriccion=0
        
            numCamion=state[-1][5]
            if action ==0:
                numCamion+=1
                
                if numCamion>Camiones:
                    numCamion=1
               
            #Si solamente hay un camión cambiar de día cada que complete una ruta  
            if Camiones==1:
                    if dia != state[-1][6]:
                        if self.rampas==1:
                            for i in range(len(tiempos)):
                                tiempos[i]=nTiempo
                                tiempos[i]-=(i+1)
                                tiempoRestante=nTiempo-1
                        if self.rampas==2:
                            for i in range(0, len(tiempos), self.rampas):
                                tiempos[i] = tiempos[i + 1] = (tiempos[i]-(i+1))

            
            #Si hay dos camiones o más cambiar de día hasta que todos hayan completado una ruta
            if Camiones != state[-1][5]:
                
                tiempoRestante=state[-1][4][numCamion-1]
                for i in range(len(tiempos)):
                    tiempos[numCamion-1]=tiempoRestante
                    tiempos[i]=nTiempo-1
                if numCamion==1:
                    dia+=1
                    if self.rampas==1:
                        for i in range(len(tiempos)):
                            tiempos[i]=nTiempo
                            tiempos[i]-=(i+1)
                            tiempoRestante=nTiempo-1
                    if self.rampas==2:
                        for i in range(0, len(tiempos), self.rampas):
                            tiempos[i] = tiempos[i + 1] = (tiempos[i]-(i+1))


            tiempos=tuple(tiempos)
            

            
            
            

            

            #Lista para guardar toda la información del resultado
            traslado=list()
            traslado.append(action)
            traslado.append(demand)
            traslado.append(volumenTrasladado)
            traslado.append(tiempoRestante)
            traslado.append(tiempos)
            traslado.append(numCamion)
            traslado.append(dia)
            
            traslado=tuple(traslado)
            s.append(traslado)
            
            state=tuple(s)
        
            
            
            

            return state

        def is_goal(self, state):
            """ 
                Determinar si el estado es el estado meta.

                state: Lista con los pedidos entregados.
            """
            
        
            entregado=copy.deepcopy(E)
            
            #Llenar la lista con los pedidos entregados
            for i in state:
                if(i[0]!=0):
                    entregado[i[0]]["Unidades"]+=i[1][0][1]
            
        
            #Si la lista de pedidos entregados está completa, entonces buscar la forma de regresar a la base
            if   entregado==dCompra:
                if state[-1][0]==0:
                    return True
            else:

                return False
            
        def cost(self, state, action, state2):
            """ 
                Este método recibe el estado y una acción, y regresa el costo de 
                aplicar la acción al estado

                state: nodo actual
                action: nodo a donde me muevo
            """
            return dict_from_dr[state[-1][0]][action] #Regresar el costo de la acción de acuerdo con la distancia en carro real
            
        def heuristic(self, state):
            """ 
                Este método regresa un estimado de la distancia desde el estado a la meta.

                Lo logra calculando la distancia en línea recta desde la base hasta cada uno de los nodos que faltan por entregarles su paquete
            """
        
            listo=[]
            for i in state:
                if i[0]!=0:
                    listo.append((i[0]))
            L=list(dict_from_df[0].keys())
            L=L[:nClientes]
            
            for i in listo:
                if i in L:
                    L.remove(i)
            suma=0
            for i in L:
                suma+=dict_from_df[0][i]
            

            return suma
            

            
            
        
        

    # Despliega los resultados
    def display(result):
        
        if result is not None:
            for i, (action, state) in enumerate(result.path()):
                if action == None:
                    print('Configuración inicial')
                elif i == len(result.path()) - 1:
                    print(i,'- Después de moverse a', action)
                    print('¡Meta lograda con costo =', result.cost,'!')
                else:
                    print(i,'- Después de moverse a', action)

                print('  ', state)
                Rutas=state
            return Rutas
        else:
            print('Mala configuración del problema')
            return 0

    #---------------------------------------------------------------------------------------------------------------
    #   Programa
    #---------------------------------------------------------------------------------------------------------------

    #---------------------------------------------------------------------------------------------------------------
    #   Programa
    #---------------------------------------------------------------------------------------------------------------



    my_viewer = None
    my_viewer = BaseViewer()       # Solo estadísticas
    #my_viewer = ConsoleViewer()    # Texto en la consola
    #my_viewer = WebViewer()        # Abrir en un browser en la liga http://localhost:8000

    # Crea un PSA y lo resuelve con la búsqueda greedy
    result = greedy(Tour('Paris'), graph_search=True, viewer=my_viewer)
 


    if my_viewer != None:
        print('Stats:')
        print(my_viewer.stats)

    print()

    print('>> Búsqueda Greedy <<')
    Rutas=display(result)



    #---------------------------------------------------------------------------------------------------------------
    #   Fin del archivo
    #---------------------------------------------------------------------------------------------------------------0.

    #Regresar resultados
    Trayecto=[]
    RutaCompleta=[]
    contadorR=0
    n=0
    sumVol=0
    sumTiempo=0
    sumdias=0
    for i in range(len(Rutas)):
        if Rutas[i][0] == 0 and n>0 :
            contadorR+=1
            numRuta=('R'+str(contadorR))
            numCamion=('C'+str(Rutas[i-1][5]))
            dia=("Dia: "+str(Rutas[i-1][6]))
            sobVol=("Sobrante m3: "+str(Rutas[i-1][2]))
            sobTiempo=("Sobrante hr: "+str(Rutas[i-1][3]))
            sumVol+=Rutas[i-1][2]
            sumTiempo+=Rutas[i-1][3]
            sumdias=Rutas[i-1][6]
            RutaCompleta.append(numRuta)
            RutaCompleta.append(numCamion)
            RutaCompleta.append(dia)
            RutaCompleta.append(sobVol)
            RutaCompleta.append(sobTiempo)
            RutaCompleta.append(Trayecto)
            Trayecto=[]
            
        
        Trayecto.append(Rutas[i][0])
        n+=1
        
    promVol=sumVol/contadorR
    promTiempo=sumTiempo/contadorR  

    print(RutaCompleta)
    print(result.cost)
    print(promVol)
    print(promTiempo)
    print(sumdias)
    print(contadorR)
    return result.cost,promVol,promTiempo,sumdias,contadorR

sumaC=0
sumaV=0
sumaT=0
sumaD=0
sumaR=0
conteo=0
for i in range(numSimulaciones):
    C,V,T,D,R=simulacion()
    sumaC+=C
    sumaV+=V
    sumaT+=T
    sumaD+=D
    sumaR+=R
    conteo+=1
    print("Sim #",conteo)
promedioC=sumaC/conteo
promedioV=sumaV/conteo
promedioT=sumaT/conteo
promedioD=sumaD/conteo
promedioR=sumaR/conteo
print("Promedio Costo: ",promedioC)
print("Promedio Volumen sobrante: ",promedioV)
print("Promedio Tiempo sobrante: ",promedioT)
print("Promedio Dias: ",promedioD)
print("Promedio Num Rutas: ",promedioR)


