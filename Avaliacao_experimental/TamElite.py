#!/usr/bin/env python
# coding: utf-8

# In[1]:


import argparse
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
def algoritmoGeneticoPlot(populacao, quantidadeCaminhos, tamanhoElite, taxaMutacao, geracoes):
    pop = populacaoInicial(quantidadeCaminhos, populacao)    
    print("Distância Inicial (Não otimizada): " + str(1 / rankRotas(pop)[0][1]))
    progresso = []
    progresso.append(1 / rankRotas(pop)[0][1])
    
    for i in range(0, tamanhoElite):
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
    plt.title("Tamanho da Elite utilizado para medir o impacto: %s" %tamanhoElite)
    plt.ylabel('Distância')
    plt.xlabel('Tamanho da Elite')
    print("\n")
    plt.show()


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

#dataset lin105
lin105 = [
    Rua(63,71),
    Rua(94,71),
    Rua(142,370),
    Rua(173,1276),
    Rua(205,1213),
    Rua(213,69),
    Rua(244,69),
    Rua(276,630),
    Rua(283,732),
    Rua(362,69),
    Rua(394,69),
    Rua(449,370),
    Rua(480,1276),
    Rua(512,1213),
    Rua(528,157),
    Rua(583,630),
    Rua(591,732),
    Rua(638,654),
    Rua(638,496),
    Rua(669,142),
    Rua(677,315),
    Rua(677,496),
    Rua(677,654),
    Rua(709,654),
    Rua(709,496),
    Rua(709,315),
    Rua(701,142),
    Rua(764,220),
    Rua(811,189),
    Rua(843,173),
    Rua(858,370),
    Rua(890,1276),
    Rua(921,1213),
    Rua(992,630),
    Rua(1000,732),
    Rua(1197,1276),
    Rua(1228,1213),
    Rua(1276,205),
    Rua(1299,630),
    Rua(1307,732),
    Rua(1362,654),
    Rua(1362,496),
    Rua(1362,291),
    Rua(1425,654),
    Rua(1425,496),
    Rua(1425,291),
    Rua(1417,173),
    Rua(1488,291),
    Rua(1488,496),
    Rua(1488,654),
    Rua(1551,654),
    Rua(1551,496),
    Rua(1551,291),
    Rua(1614,291),
    Rua(1614,496),
    Rua(1614,654),
    Rua(1732,189),
    Rua(1811,1276),
    Rua(1843,1213),
    Rua(1913,630),
    Rua(1921,732),
    Rua(2087,370),
    Rua(2118,1276),
    Rua(2150,1213),
    Rua(2189,205),
    Rua(2220,189),
    Rua(2220,630),
    Rua(2228,732),
    Rua(2244,142),
    Rua(2276,315),
    Rua(2276,496),
    Rua(2276,654),
    Rua(2315,654),
    Rua(2315,496),
    Rua(2315,315),
    Rua(2331,142),
    Rua(2346,315),
    Rua(2346,496),
    Rua(2346,654),
    Rua(2362,142),
    Rua(2402,157),
    Rua(2402,220),
    Rua(2480,142),
    Rua(2496,370),
    Rua(2528,1276),
    Rua(2559,1213),
    Rua(2630,630),
    Rua(2638,732),
    Rua(2756,69),
    Rua(2787,69),
    Rua(2803,370),
    Rua(2835,1276),
    Rua(2866,1213),
    Rua(2906,69),
    Rua(2937,69),
    Rua(2937,630),
    Rua(2945,732),
    Rua(3016,1276),
    Rua(3055,69),
    Rua(3087,69),
    Rua(606,220),
    Rua(1165,370),
    Rua(1780,370)
    ]
# In[14]:
# algoritmoGeneticoPlot(listas[populacao], quantidadeCaminhos, tamanhoElite, taxaMutacao, geracoes)

#----------------------------------------
#Script para orquestrar a realização de experimentos
start_time = tm.time()
algoritmoGeneticoPlot(berlin52, 200, 10, 0.001, 200)
x1 = 10
y1 = tmp

start_time = tm.time()
algoritmoGeneticoPlot(berlin52, 200, 30, 0.001, 200)
x2 = 30
y2 = tmp

start_time = tm.time()
algoritmoGeneticoPlot(berlin52, 200, 50, 0.001, 200)
x3 = 50
y3 = tmp

start_time = tm.time()
algoritmoGeneticoPlot(berlin52, 200, 70, 0.001, 200)
x4 = 70
y4 = tmp

start_time = tm.time()
algoritmoGeneticoPlot(berlin52, 200, 90, 0.001, 200)
x5 = 90
y5 = tmp

#Script para gerar o gráfico de tempo de execução tendo em vista o tamanho do elitismo
def tempoExecucao():
    x=[x1,x2,x3,x4,x5]
    y=[y1,y2,y3,y4,y5]
    plt.plot(x,y)
    plt.scatter(x,y, color='blue')
    plt.xlabel("Tamanho do Elitismo")    
    plt.ylabel("Tempo de execução (s)")
    plt.title("Tempo de execução em relação ao Tamanho do Elitismo")
    plt.show()

tempoExecucao()