# ============================================================
# EXERCICIO 1 - FILTRO DE BLOOM
# ============================================================

class FiltroBloom:

    def __init__(self, tamanho=11):
        self.M = tamanho
        # a) Vetor de bits (array de inteiros) inicializado com 0
        self.bits = [0] * self.M

    # b) Funcoes de dispersao
    def h1(self, x):
        return x % 11

    def h2(self, x):
        return (2 * x + 3) % 11

    def h3(self, x):
        return (7 * x + 1) % 11

    def _posicoes(self, x):
        # Retorna as tres posicoes de bit associadas ao ID x.
        return [self.h1(x), self.h2(x), self.h3(x)]

    def inserir(self, x):
        posicoes = self._posicoes(x)
        for p in posicoes:
            self.bits[p] = 1
        print(f"Inserido ID {x} -> bits ligados nas posicoes {posicoes}")

    def consultar(self, x):
        """
        Verifica se o ID PODE estar no conjunto.
        Retorna True  -> "provavelmente existe" (todas as posicoes = 1)
        Retorna False -> "definitivamente nao existe" (alguma posicao = 0)
        """
        posicoes = self._posicoes(x)
        valores = [self.bits[p] for p in posicoes]
        provavelmente_existe = all(v == 1 for v in valores)
        print(f"Consulta ID {x}: posicoes {posicoes} -> bits {valores} "
              f"=> {'PROVAVELMENTE EXISTE' if provavelmente_existe else 'DEFINITIVAMENTE NAO EXISTE'}")
        return provavelmente_existe

    def imprimir(self):
        print(f"Vetor de bits final (M={self.M}): {self.bits}")


def exercicio1():

    print("EXERCICIO 1 - FILTRO DE BLOOM")

    bloom = FiltroBloom(tamanho=11)

    # c) Insercao dos IDs de ameacas conhecidas
    print("\n--- Insercao das ameacas conhecidas ---")
    for id_ameaca in [15, 22, 45]:
        bloom.inserir(id_ameaca)
    bloom.imprimir()

    # d) Verificacao dos IDs 10 e 22
    print("\n--- Verificacao de trafego ---")
    resultado_10 = bloom.consultar(10)   # trafego normal
    if not resultado_10:
        print("-> ID 10: o filtro descartou o IP IMEDIATAMENTE")

    resultado_22 = bloom.consultar(22)   # trafego suspeito
    if resultado_22:
        print("-> ID 22: o filtro sinalizou 'provavel ameaca', entao o "
              "sistema deve prosseguir para a busca na Tabela Hash "
              "para confirmar.")

    # e) Consulta ao ID 37 (nao inserido)
    print("\n--- Analise do ID 37 (nao inserido) ---")
    resultado_37 = bloom.consultar(37)
    '''
     Comentario/explicacao pedida no item e:
     O ID 37 nunca foi inserido no filtro, mas suas tres posicoes de
     hash (h1, h2, h3) coincidem, por acaso, com posicoes que ja
     haviam sido marcadas com 1 pelas insercoes de 15, 22 e 45.
     Isso faz o filtro reportar "provavelmente existe" para um
     elemento que na verdade NAO esta na lista de bloqueio: um FALSO
     POSITIVO. Isso e aceitavel na engenharia do sistema porque o
     Filtro de Bloom e apenas uma otimizacao de pre-filtragem: um
     falso positivo so custa uma busca extra (e descartavel) na
     Tabela Hash real, que ira confirmar que o ID 37 nao e uma
     ameaca. O que o filtro NUNCA pode fazer e um falso negativo
     (dizer que um IP malicioso conhecido nao esta na lista), e essa
     garantia se mantem.
    '''
    if resultado_37:
        print("-> Isso e um FALSO POSITIVO (ver comentario no codigo). "
              "E aceitavel pois apenas gera uma busca extra na Tabela "
              "Hash, que descartara o ID corretamente.")


# ============================================================
# EXERCICIO 2 - TABELA HASH (N = 7, h(x) = x mod 7)
# ============================================================

N = 7
SEQUENCIA = [10, 17, 24, 31, 5, 12]


def h(x):
    return x % N


# ---------- Parte A: Encadeamento Externo (Hashing Aberto) ----------

class NoExterno:
    # No de lista encadeada alocado dinamicamente (fora do array).
    def __init__(self, chave):
        self.chave = chave
        self.proximo = None


class TabelaEncadeamentoExterno:
    """
    Cada posicao do array principal guarda apenas um PONTEIRO para o
    inicio de uma lista encadeada. Os dados ficam fora do array, em
    memoria alocada dinamicamente (heap).
    """
    def __init__(self, tamanho):
        self.tamanho = tamanho
        self.tabela = [None] * tamanho

    def inserir(self, chave):
        idx = h(chave)
        novo = NoExterno(chave)
        if self.tabela[idx] is None:
            # Começa a lista encadeada
            self.tabela[idx] = novo
        else:
            # Insere no fim da lista encadeada
            atual = self.tabela[idx]
            while atual.proximo is not None:
                atual = atual.proximo
            atual.proximo = novo

    def imprimir(self):
        print("Indice | Array principal -> Lista externa")
        for i in range(self.tamanho):
            cadeia = []
            atual = self.tabela[i]
            while atual is not None:
                cadeia.append(str(atual.chave))
                atual = atual.proximo
            if cadeia:
                print(f"  [{i}]   ->  " + " -> ".join(cadeia) + " -> NULL")
            else:
                print(f"  [{i}]   ->  NULL")


# ---------- Parte B: Encadeamento Interno Coalescido ----------

class NoInterno:
    """Estrutura do no: [ID da Ameaca | Ponteiro(indice) para o Proximo]."""
    def __init__(self):
        self.chave = None       # None = posicao vazia
        self.proximo = None     # indice do proximo no da cadeia (ou None)
        self.lapide = False     # marca de remocao (usada no Exercicio 3)


class TabelaCoalescida:
    """
    Encadeamento interno coalescido: todos os dados ficam DENTRO do
    proprio array (nao ha alocacao externa). Quando ocorre colisao, o
    novo elemento e colocado no ultimo espaco vazio do array
    (varrendo de baixo para cima) e o ponteiro 'proximo' do ultimo nó
    da cadeia do indice de origem e atualizado para apontar para essa
    nova posicao.
    """
    def __init__(self, tamanho):
        self.tamanho = tamanho
        self.tabela = [NoInterno() for _ in range(tamanho)]

    def _proximo_espaco_vazio(self):
        # Varre o array de baixo para cima e retorna o ultimo indice vazio.
        for i in range(self.tamanho - 1, -1, -1):
            if self.tabela[i].chave is None:
                return i
        return None

    def inserir(self, chave):
        idx = h(chave)

        if self.tabela[idx].chave is None:
            # Posicao inicial livre: insere diretamente (sem colisao)
            self.tabela[idx].chave = chave
            return

        # Colisao: procura o ultimo espaco vazio do array (de baixo p/ cima)
        novo_idx = self._proximo_espaco_vazio()
        if novo_idx is None:
            print("Tabela cheia! Nao foi possivel inserir", chave)
            return

        self.tabela[novo_idx].chave = chave

        '''
        Encontra o ULTIMO no da cadeia que comeca fisicamente em idx
        (essa cadeia pode ja conter elementos de OUTRAS chaves-lar,
        que foi para onde acabaram coalescendo) e liga o ponteiro
        do ultimo no dessa cadeia para o novo indice.
        '''
        atual = idx
        while self.tabela[atual].proximo is not None:
            atual = self.tabela[atual].proximo
        self.tabela[atual].proximo = novo_idx

    def buscar(self, chave):
        """
        Busca uma chave a partir do seu endereco de origem h(chave),
        percorrendo a cadeia de ponteiros internos. Posicoes marcadas
        com Lapide sao ignoradas (puladas), mas o ponteiro delas e
        respeitado para nao quebrar a cadeia.
        """
        idx = h(chave)
        passos = [idx]
        while idx is not None:
            no = self.tabela[idx]
            if no.chave == chave and not no.lapide:
                return True, passos
            idx = no.proximo
            if idx is not None:
                passos.append(idx)
        return False, passos

    def remover(self, chave):
        """
        Remocao com tecnica de Lapide: mantem o
        ponteiro 'proximo' intacto para nao quebrar a cadeia de
        busca de outras chaves que dependam desse elo.
        """
        idx = h(chave)
        while idx is not None:
            no = self.tabela[idx]
            if no.chave == chave and not no.lapide:
                no.lapide = True   # marca como removido (nao apaga o proximo!)
                return True
            idx = no.proximo
        return False

    def imprimir(self):
        print(" Indice | Chave       | Proximo")
        for i, no in enumerate(self.tabela):
            if no.chave is None:
                chave_str = "-- vazio --"
            elif no.lapide:
                chave_str = f"[LAPIDE] ({no.chave})"
            else:
                chave_str = str(no.chave)
            proximo_str = str(no.proximo) if no.proximo is not None else "NULL"
            print(f"  [{i}]   | {chave_str:<12}| -> {proximo_str}")


def exercicio2():

    print("EXERCICIO 2 - TABELA HASH (N=7, h(x)=x mod 7)")

    print(f"\nSequencia de insercao: {SEQUENCIA}")
    print("Enderecos h(x):", {x: h(x) for x in SEQUENCIA})

    print("\n--- Parte A: Encadeamento Externo (Hashing Aberto) ---")
    tabela_a = TabelaEncadeamentoExterno(N)
    for chave in SEQUENCIA:
        tabela_a.inserir(chave)
    tabela_a.imprimir()

    print("\n--- Parte B: Encadeamento Interno Coalescido (Hashing Fechado) ---")
    tabela_b = TabelaCoalescida(N)
    for chave in SEQUENCIA:
        tabela_b.inserir(chave)
    tabela_b.imprimir()

    print("\n--- Parte C: Analise Critica ---")
    '''
    Comentario pedido no item Parte C:
    A Parte A (Encadeamento Externo) causaria MAIS lentidao de I/O
    em disco. Isso porque cada no da lista encadeada e alocado
    dinamicamente em um endereco de memoria/disco arbitrario, sem
    relacao de proximidade fisica com o array principal nem entre
    si. Cada "atual = atual.proximo" da travessia da lista pode
    exigir uma nova leitura de bloco de disco em uma regiao
    totalmente diferente. Ja a Parte B
    (Encadeamento Interno Coalescido) mantem todos os dados dentro
    de um unico array continuo em disco: mesmo seguindo os
    ponteiros internos, o sistema operacional tende a manter esse
    bloco de dados proximo ou ja em cache,
    reduzindo drasticamente o numero de acessos aleatorios ao
    disco. Logo, a Parte A e a mais custosa em um cenario de disco
    rigido real.
    '''
    print("Ver bloco de comentarios no codigo-fonte (funcao exercicio2) "
          "com a analise completa. Resumo: o Encadeamento Externo "
          "(Parte A) e mais lento em disco por espalhar os nos em "
          "posicoes de memoria arbitrarias; "
          "o Encadeamento Interno Coalescido (Parte B) mantem "
          "tudo em um bloco continuo, favorecendo a localidade.")

    return tabela_b  # Reaproveitada no Exercicio 3


# ============================================================
# EXERCICIO 3 - REMOCAO COM LAPIDE NA TABELA COALESCIDA
# ============================================================

def exercicio3(tabela_b):
    print("\n" + "=" * 60)
    print("EXERCICIO 3 - REMOCAO COM TECNICA DE LAPIDE (TOMBSTONE)")
    print("=" * 60)

    # a) Remove o ID 24 usando Lapide
    print("\n--- a) Removendo ID 24 (tecnica de Lapide) ---")
    ok = tabela_b.remover(24)
    print("Remocao com sucesso!" if ok else "ID nao encontrado.")

    # b) Imprime a tabela apos a remocao
    print("\n--- b) Tabela apos a remocao ---")
    tabela_b.imprimir()

    # c) Busca o ID 31
    print("\n--- c) Buscando ID 31 apos a remocao ---")
    encontrado, caminho = tabela_b.buscar(31)
    print(f"Caminho percorrido (indices): {caminho}")
    if encontrado:
        print("Sim! O ID 31 foi encontrado com sucesso, mesmo pulando "
              "a Lapide deixada pelo ID 24")
    else:
        print("ID 31 nao encontrado (nao deveria acontecer).")


if __name__ == "__main__":
    exercicio1()
    tabela_b = exercicio2()
    exercicio3(tabela_b)