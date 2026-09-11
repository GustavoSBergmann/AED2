class NodoArvoreB:
    def __init__(self, grau: int, folha: bool):
        self.grau = grau
        self.folha = folha
        self.chaves = []
        self.filhos = []

class ArvoreB:
    def __init__(self, grau):
        self.raiz = NodoArvoreB(grau, True)
        self.grau = grau

    