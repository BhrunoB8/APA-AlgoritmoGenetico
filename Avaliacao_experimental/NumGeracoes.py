#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np, random, operator, pandas as pd, matplotlib.pyplot as plt
import time as tm
#Definição da classe Rua
class Rua:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    # Realiza o cálculo da distância euclidiana
    def distancia(self, rua):
      return ((self.x - rua.x) ** 2 + (self.y - rua.y) ** 2) ** 0.5

    # Imprime as coordenadas como (x,y)
    def __repr__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"


# In[2]:


#Criando uma rota de maneira aleatória
def criarRota(listaRuas):
    #rota = random.sample(listaRuas, len(listaRuas))
    rota = listaRuas
    return rota

def populacaoInicial(tamanhoPop, listaRuas):
    populacao = []

    for i in range(0, tamanhoPop):
        populacao.append(criarRota(listaRuas))
    return populacao


# In[3]:


#É realizado o cálculo para determinar o maior fitness
class Fitness:
    def __init__(self, rota):
        self.rota = rota
        self.distancia = 0
        self.fitness= 0.0
    
    def distanciaRota(self):
        if self.distancia ==0:
            distanciaRota = 0
            for i in range(0, len(self.rota)):
                ruaOrigem = self.rota[i]
                ruaDestino = None
                
                # Precisa terminar na rua onde começou, então faz essa verificação
                # se não for o último nó, adiciona a próxima "rua" a ser visitada
                if i + 1 < len(self.rota):
                    ruaDestino = self.rota[i + 1]
                # caso contrário, é o último nó e atribui o primeiro nó visitado
                else:
                    ruaDestino = self.rota[0]
                
                # calcula a distância entre a rua inicial e a próxima 
                distanciaRota += ruaOrigem.distancia(ruaDestino)

            self.distancia = distanciaRota
        return self.distancia
    
    def fitnessRota(self):
        if self.fitness == 0:
            self.fitness = 1 / float(self.distanciaRota())
        return self.fitness


# In[4]:


#Escolha do indivíduo por meio da seleção natural
def rankRotas(populacao):
    resultadosFitness = {}
    for i in range(0,len(populacao)):
        resultadosFitness[i] = Fitness(populacao[i]).fitnessRota()
    return sorted(resultadosFitness.items(), key = operator.itemgetter(1), reverse = True)


# In[5]:


# A função de seleção recebe como primeiro parâmetro a saída da função rankRotas
# para determinar qual rota utilizar
def selecao(rankedPop, tamanhoElite):
    resultadoSelecao = []
    # Aqui é feito o cálculo de peso relativo de aptidão para cada indivíduo
    df = pd.DataFrame(np.array(rankedPop), columns=["Index","Fitness"])
    df['cum_sum'] = df.Fitness.cumsum()
    df['cum_perc'] = 100*df.cum_sum/df.Fitness.sum()
    
    # Adição do elitismo
    for i in range(0, tamanhoElite):
        resultadoSelecao.append(rankedPop[i][0])
    # Aqui é feita a comparação de um número aleatório com esses pesos relativos
    # de aptidão para selecionar os indivíduos para a etapa de "Procriação"
    for i in range(0, len(rankedPop) - tamanhoElite):
        pick = 100*random.random()
        for i in range(0, len(rankedPop)):
            if pick <= df.iat[i,3]:
                resultadoSelecao.append(rankedPop[i][0])
                break
    return resultadoSelecao

# Essa função pega o resultado da nossa seleção anterior e busca estes indivíduos
# da nossa população
def procriacao(populacao, resultadoSelecao):
    procriacao = []
    for i in range(0, len(resultadoSelecao)):
        index = resultadoSelecao[i]
        procriacao.append(populacao[index])
    return procriacao


# In[6]:


#É realizada a criação da próxima geração por meio do crossover
#em que é escolhido qual o gene vai ser pego de cada pai
def geracao(parente1, parente2):
    filho = []
    filhoP1 = []
    filhoP2 = []
    
    geneA = int(random.random() * len(parente1))
    geneB = int(random.random() * len(parente1))
    
    startGene = min(geneA, geneB)
    endGene = max(geneA, geneB)

    # Aqui é feita a escolha do subconjunto aleatório do primeiro pai
    for i in range(startGene, endGene):
        filhoP1.append(parente1[i])
        
    # Se o gene não existe no primeiro pai, então pega do segundo pai
    filhoP2 = [item for item in parente2 if item not in filhoP1]

    filho = filhoP1 + filhoP2
    return filho


# In[7]:


def gerarPopulacao(procriacao, tamanhoElite):
    filhos = []
    tamanho = len(procriacao) - tamanhoElite
    pool = random.sample(procriacao, len(procriacao))

    # Aqui novamente usamos o elitismo para manter as melhores rotas/indivíduos 
    for i in range(0,tamanhoElite):
        filhos.append(procriacao[i])
    # Aqui utilizamos a função de geracao mencionada acima para preencher o resto
    # dos indivíduos
    for i in range(0, tamanho):
        filho = geracao(pool[i], pool[len(procriacao)-i-1])
        filhos.append(filho)
    return filhos


# In[8]:


#É feita uma exploração para encontrar novas soluções
#utilizando o swap para percorrer diferentes ruas
def mutacao(individual, taxaMutacao):
    for swapped in range(len(individual)):
        if(random.random() < taxaMutacao):
            swapWith = int(random.random() * len(individual))
            
            rua1 = individual[swapped]
            rua2 = individual[swapWith]
            
            individual[swapped] = rua2
            individual[swapWith] = rua1
    return individual


# In[9]:


# Aqui a mutação é aplicada na população
def mutacaoPopulacao(populacao, taxaMutacao):
    populacaoMutada = []
    
    for individuo in range(0, len(populacao)):
        individuoMutado = mutacao(populacao[individuo], taxaMutacao)
        populacaoMutada.append(individuoMutado)
    return populacaoMutada


# In[10]:


#Aqui é feita a escolha do indivíduo, mais apto, por meio da função rankRotas
#em seguida a escolha dos potenciais pais com a função de selecao
#posteriormente é feito o processo de matingpool onde é pego as soluções candidatas, pela função procriacao
#após isto é realizado a procriação gerando novos "filhos", por meio da função gerarPopulacao
#e por fim é aplicada a mutação utilizando a função mutacaoPopulacao
def proximaGeracao(geracaoAtual, tamanhoElite, taxaMutacao):
    rankedPop = rankRotas(geracaoAtual)
    resultadoSelecao = selecao(rankedPop, tamanhoElite)
    procriacaoa = procriacao(geracaoAtual, resultadoSelecao)
    filhos = gerarPopulacao(procriacaoa, tamanhoElite)
    proximaGeracao = mutacaoPopulacao(filhos, taxaMutacao)
    return proximaGeracao


# In[11]:


def algoritmoGenetico(populacao, quantidadeCaminhos, tamanhoElite, taxaMutacao, geracoes):
    pop = populacaoInicial(quantidadeCaminhos, populacao)
    print("Distancia Inicial: " + str(1 / rankRotas(pop)[0][1]))
    
    for i in range(0, geracoes):
        pop = proximaGeracao(pop, tamanhoElite, taxaMutacao)
    
    print("Final distancia: " + str(1 / rankRotas(pop)[0][1]))
    melhorRotaIndex = rankRotas(pop)[0][0]
    melhorRota = pop[melhorRotaIndex]
    return melhorRota


# In[12]:


#Plotagem do gráfico do Algoritmo Genético
tmp = 0
def algoritmoGeneticoPlot(populacao, quantidadeCaminhos, tamanhoElite, taxaMutacao, geracoes):
    pop = populacaoInicial(quantidadeCaminhos, populacao)    
    print("Distância Inicial (Não otimizada): " + str(1 / rankRotas(pop)[0][1]))
    progresso = []
    progresso.append(1 / rankRotas(pop)[0][1])
    
    for i in range(0, geracoes):
        pop = proximaGeracao(pop, tamanhoElite, taxaMutacao)
        progresso.append(1 / rankRotas(pop)[0][1])
    
    print("Distância Final (Otimizada): " + str(1 / rankRotas(pop)[0][1]))
    melhorRotaIndex = rankRotas(pop)[0][0]
    melhorRota = pop[melhorRotaIndex]
    print("Melhor rota:", melhorRota)
    global tmp
    tmp = (tm.time() - start_time)
    print("Tempo de Execução: %s segundos" %tmp)
    plt.plot(progresso)
    plt.title("Número de Gerações utilizado para medir o impacto: %s" %geracoes)
    plt.ylabel('Distância')
    plt.xlabel('Número de Gerações')
    print("\n")
    plt.show()

# def tempoExecucao(populacao):
#     y= (tm.time() - start_time)
#     x= populacao
#     plt.scatter(x,y)
#     plt.show()


# In[13]:
     
    #dataset berlin52 (Groetschel)
berlin52=[Rua(565,575),
    Rua(25,185),
    Rua(345,750),
    Rua(945,685),
    Rua(845,655),
    Rua(880,660),
    Rua(25,230),
    Rua(525,1000),
    Rua(580,1175),
    Rua(650,1130),
    Rua(1605,620),
    Rua(1220,580),
    Rua(1465,200),
    Rua(1530,5),
    Rua(845,680),
    Rua(725,370),
    Rua(145,665),
    Rua(415,635),
    Rua(510,875),
    Rua(560,365),
    Rua(300,465),
    Rua(520,585),
    Rua(480,415),
    Rua(835,625),
    Rua(975,580),
    Rua(1215,245),
    Rua(1320,315),
    Rua(1250,400),
    Rua(660,180),
    Rua(410,250),
    Rua(420,555),
    Rua(575,665),
    Rua(1150,1160),
    Rua(700,580),
    Rua(685,595),
    Rua(685,610),
    Rua(770,610),
    Rua(795,645),
    Rua(720,635),
    Rua(760,650),
    Rua(475,960),
    Rua(95,260),
    Rua(875,920),
    Rua(700,500),
    Rua(555,815),
    Rua(830,485),
    Rua(1170,65),
    Rua(830,610),
    Rua(605,625),
    Rua(595,360),
    Rua(1340,725),
    Rua(1740,245)]
    
    #dataset st60
st60 = [Rua(64,96),
    Rua(80,39),
    Rua(69,23),
    Rua(72,42),
    Rua(48,67),
    Rua(58,43),
    Rua(81,34),
    Rua(79,17),
    Rua(30,23),
    Rua(42,67),
    Rua(7,76),
    Rua(29,51),
    Rua(78,92),
    Rua(64,8),
    Rua(95,57),
    Rua(57,91),
    Rua(40,35),
    Rua(68,40),
    Rua(92,34),
    Rua(62,1),
    Rua(28,43),
    Rua(76,73),
    Rua(67,88),
    Rua(93,54),
    Rua(6,8),
    Rua(87,18),
    Rua(30,9),
    Rua(77,13),
    Rua(78,94),
    Rua(55,3),
    Rua(82,88),
    Rua(73,28),
    Rua(20,55),
    Rua(27,43),
    Rua(95,86),
    Rua(67,99),
    Rua(48,83),
    Rua(75,81),
    Rua(8,19),
    Rua(20,18),
    Rua(54,38),
    Rua(63,36),
    Rua(44,33),
    Rua(52,18),
    Rua(12,13),
    Rua(25,5),
    Rua(58,85),
    Rua(5,67),
    Rua(90,9),
    Rua(41,76),
    Rua(25,76),
    Rua(37,64),
    Rua(56,63),
    Rua(10,55),
    Rua(98,7),
    Rua(16,74),
    Rua(89,60),
    Rua(48,82),
    Rua(81,76),
    Rua(29,60),
    Rua(17,22),
    Rua(5,45),
    Rua(79,70),
    Rua(9,100),
    Rua(17,82),
    Rua(74,67),
    Rua(10,68),
    Rua(48,19),
    Rua(83,86),
    Rua(84,94)]
#bayg29 - 29 Cities in Bavaria, geographical distances (Groetschel,Juenger,Reinelt)
bayg29 = [
    Rua(1150,1760),
    Rua(630,1660),
    Rua(40,2090),
    Rua(750,1100),
    Rua(750,2030),
    Rua(1030,2070),
    Rua(1650,650),
    Rua(1490,1630),
    Rua(790,2260),
    Rua(710,1310),
    Rua(840,550),
    Rua(1170,2300),
    Rua(970,1340),
    Rua(510,700),
    Rua(750,900),
    Rua(1280,1200),
    Rua(230,590),
    Rua(460,860),
    Rua(1040,950),
    Rua(590,1390),
    Rua(830,1770),
    Rua(490,500),
    Rua(1840,1240),
    Rua(1260,1500),
    Rua(1280,790),
    Rua(490,130),
    Rua(1460,1420),
    Rua(1260,1910)]
 

#kroB200 - 
kroB150 = [
    Rua(1357, 1905),
    Rua(2650, 802),
    Rua(1774, 107),
    Rua(1307, 964),
    Rua(3806, 746),
    Rua(2687, 1353),
    Rua(43, 1957),
    Rua(3092, 1668),
    Rua(185, 1542),
    Rua(834, 629),
    Rua(40, 462),
    Rua(1183, 1391),
    Rua(2048, 1628),
    Rua(1097, 643),
    Rua(1838, 1732),
    Rua(234, 1118),
    Rua(3314, 1881),
    Rua(737, 1285),
    Rua(779, 777),
    Rua(2312, 1949),
    Rua(2576, 189),
    Rua(3078, 1541),
    Rua(2781, 478),
    Rua(705, 1812),
    Rua(3409, 1917),
    Rua(323, 1714),
    Rua(1660, 1556),
    Rua(3729, 1188),
    Rua(693, 1383),
    Rua(2361, 640),
    Rua(2433, 1538),
    Rua(554, 1825),
    Rua(913, 317),
    Rua(3586, 1909),
    Rua(2636, 727),
    Rua(1000, 457),
    Rua(482,1337),
    Rua(3704, 1082),
    Rua(3635, 1174),
    Rua(1362, 1526),
    Rua(2049, 417),
    Rua(2552, 1),
    Rua(219, 898),
    Rua(812, 351),
    Rua(901, 1552),
    Rua(2513, 1572),
    Rua(242, 584),
    Rua(826, 1226),
    Rua(3278, 799),
    Rua(86, 1065),
    Rua(14, 454),
    Rua(1327, 1893),
    Rua(2773,1286),
    Rua(2469, 1838),
    Rua(3835, 963),
    Rua(1031, 428),
    Rua(3853, 1712),
    Rua(1868, 197),
    Rua(1544, 863),
    Rua(457, 1607),
    Rua(3174, 1064),
    Rua(192, 1004),
    Rua(2318, 1925),
    Rua(2232, 1374),
    Rua(396,828),
    Rua(2365, 1649),
    Rua(2499, 658),
    Rua(1410, 307),
    Rua(2990, 214),
    Rua(3646, 1018),
    Rua(3394, 1028),
    Rua(1779, 90),
    Rua(1058, 372),
    Rua(2933, 1459),
    Rua(3099, 173),
    Rua(2178, 978),
    Rua(138, 1610),
    Rua(2082, 1753),
    Rua(2302, 1127),
    Rua(805, 272),
    Rua(22, 1617),
    Rua(3213, 1085),
    Rua(99, 536),
    Rua(1533, 1780),
    Rua(3564, 676),
    Rua(29, 6),
    Rua(3808, 1375),
    Rua(2221, 291),
    Rua(3499, 1885),
    Rua(3124, 408),
    Rua(781, 671),
    Rua(1027, 1041),
    Rua(3249, 378),
    Rua(3297, 491),
    Rua(213, 220),
    Rua(721, 186),
    Rua(3736, 1542),
    Rua(868, 731),
    Rua(960, 303),
    Rua(3825, 1101),
    Rua(2779, 435),
    Rua(201, 693),
    Rua(2502, 1274),
    Rua(765, 833),
    Rua(3105, 1823),
    Rua(1937, 1400),
    Rua(3364, 1498),
    Rua(3702, 1624),
    Rua(2164, 1874),
    Rua(3019, 189),
    Rua(3098, 1594),
    Rua(3239, 1376),
    Rua(3359, 1693),
    Rua(2081, 1011),
    Rua(1398, 1100),
    Rua(618, 1953),
    Rua(1878, 59),
    Rua(3803, 886),
    Rua(397, 1217),
    Rua(3035,152),
    Rua(2502, 146),
    Rua(3230,380),
    Rua(3479, 1023),
    Rua(958, 1670),
    Rua(3423, 1241),
    Rua(78, 1066),
    Rua(96, 691),
    Rua(3431, 78),
    Rua(2053, 1461),
    Rua(3048, 1),
    Rua(571, 1711),
    Rua(3393, 782),
    Rua(2835, 1472),
    Rua(144, 1185),
    Rua(923, 108),
    Rua(989, 1997),
    Rua(3061, 1211),
    Rua(2977, 39),
    Rua(1668, 658),
    Rua(878, 715),
    Rua(678, 1599),
    Rua(1086, 868),
    Rua(640, 110),
    Rua(3551, 1673),
    Rua(106, 1267),
    Rua(2243, 1332),
    Rua(3796, 1401),
    Rua(2643, 1320),
    Rua(48, 267)]

    
# In[14]:
# algoritmoGeneticoPlot(listas[populacao], quantidadeCaminhos, tamanhoElite, taxaMutacao, geracoes)

#Script para orquestrar a realização de experimentos
start_time = tm.time()
algoritmoGeneticoPlot(berlin52, 200, 55, 0.001, 200)
x1=200
y1= tmp

start_time = tm.time()
algoritmoGeneticoPlot(berlin52, 200, 55, 0.001, 400)
x2=400
y2= tmp

start_time = tm.time()
algoritmoGeneticoPlot(berlin52, 200, 55, 0.001, 600)
x3=600
y3= tmp

start_time = tm.time()
algoritmoGeneticoPlot(berlin52, 200, 55, 0.001, 800)
x4=800
y4= tmp

start_time = tm.time()
algoritmoGeneticoPlot(berlin52, 200, 55, 0.001, 1000)
x5=1000
y5= tmp

#o gráfico de tempo de exeucução tendo em vista o número de gerações
#Script para gerar gráficos
def tempoExecucao():
    x=[x1,x2,x3,x4,x5]
    y=[y1,y2,y3,y4,y5]
    plt.plot(x,y, label="Número de Gerações")
    plt.legend()
    plt.scatter(x,y, color='blue')
    plt.xlabel("Número de gerações")
    plt.ylabel("Tempo de execução (s)")
    plt.title("Tempo de execução em relação ao Número de Gerações")
    plt.show()

tempoExecucao()

