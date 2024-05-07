import pygame
import random
from pygame.locals import *

# Define as constantes para a largura e altura da tela do jogo
LARGURA_TELA = 400
ALTURA_TELA = 800

# Largura e altura do chão
LARGURA_CHAO = 2 * LARGURA_TELA
ALTURA_CHAO = 100

# Largura e altura Tubo
LARGURA_TUBO = 120
ALTURA_TUBO = 500
INTERVALO_TUBO = 200

# Define a velocidade inicial do personagem e a gravidade que afeta o personagem
VELOCIDADE = 10
GRAVIDADE = 1

# Define a velocidade do jogo
VELOCIDADE_JOGO = 10


# Define a classe Caramelo, que herda de pygame.sprite.Sprite
# Esta classe representa o personagem principal do jogo
class Caramelo(pygame.sprite.Sprite):

    # Método construtor da classe
    def __init__(self):
        # Chama o construtor da classe pai
        pygame.sprite.Sprite.__init__(self)

        # Carrega as imagens do personagem e as armazena em uma lista
        self.imagens = [pygame.image.load('assets/bluebird-midflap.png').convert_alpha(),
                        pygame.image.load('assets/bluebird-upflap.png').convert_alpha(),
                        pygame.image.load('assets/bluebird-downflap.png').convert_alpha()]

        # Define a velocidade do personagem como a velocidade inicial
        self.velocidade = VELOCIDADE

        # Inicializa o índice da imagem atual do personagem
        self.imagem_atual = 0

        # Define a imagem inicial do personagem
        self.image = pygame.image.load('assets/bluebird-upflap.png').convert_alpha()
        # Ajusta o tamanho da imagem para preencher a tela
        self.mask = pygame.mask.from_surface(self.image)

        # Cria um retângulo para a imagem, que será usado para a posição e colisões
        self.rect = self.image.get_rect()
        # Centraliza o personagem na tela
        self.rect[0] = LARGURA_TELA / 2
        self.rect[1] = ALTURA_TELA / 2

    # Método para atualizar o estado do personagem
    def update(self):
        # Atualiza o índice da imagem para animar o personagem
        self.imagem_atual = (self.imagem_atual + 1) % 3
        self.image = self.imagens[self.imagem_atual]

        # Aplica a gravidade à velocidade do personagem
        self.velocidade += GRAVIDADE

        # Atualiza a posição vertical do personagem com base na velocidade
        self.rect[1] += self.velocidade

    # Método para fazer o personagem pular
    def pular(self):
        # Inverte a velocidade para criar um movimento de pulo
        self.velocidade = -VELOCIDADE


# Define a classe Tubo, que herda de pygame.sprite.Sprite
class Tubo(pygame.sprite.Sprite):
    def __init__(self, xpos, ysize, inverted):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load('assets/pipe-green.png')
        self.image = pygame.transform.scale(self.image, (LARGURA_TUBO, ALTURA_TUBO))

        self.rect = self.image.get_rect()
        self.rect[0] = xpos

        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect[1] = - (self.rect[3] - ysize)
        else:
            self.rect[1] = ALTURA_TELA - ysize

        # Cria uma máscara para a imagem, que será usada para colisões
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect[0] -= VELOCIDADE_JOGO


# Classe Chao herda de pygame.sprite.Sprite
class Chao(pygame.sprite.Sprite):
    # Método construtor da classe
    def __init__(self, xpos):
        # Chama o construtor da classe pai
        pygame.sprite.Sprite.__init__(self)

        # Carrega a imagem do chão
        self.image = pygame.image.load('assets/base.png')
        # Ajusta o tamanho da imagem para preencher a tela
        self.image = pygame.transform.scale(self.image, (LARGURA_CHAO, ALTURA_CHAO))

        # Cria um retângulo para a imagem, que será usado para a posição e colisões
        self.rect = self.image.get_rect()

        # Posiciona o chão na parte inferior da tela
        self.rect[0] = xpos
        self.rect[1] = ALTURA_TELA - ALTURA_CHAO

    # Método para atualizar o estado do chão
    def update(self):
        # Move o chão para a esquerda para criar a ilusão de movimento do personagem
        self.rect[0] -= VELOCIDADE_JOGO


# Função para verificar se um sprite saiu da tela
def esta_fora_da_tela(sprite):
    return sprite.rect[0] < -sprite.rect[2]


def criar_tubo_aleatorio(xpos: int) -> (Tubo, Tubo):
    tamanho = random.randint(100, 300)
    tubo = Tubo(xpos, tamanho, False)
    tubo_invertido = Tubo(xpos, ALTURA_TELA - tamanho - INTERVALO_TUBO, True)
    return tubo, tubo_invertido


def main():
    pygame.init()  # Inicializa o módulo pygame
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))  # Cria a tela do jogo com as dimensões especificadas

    # Carrega a imagem de fundo e ajusta seu tamanho para preencher a tela
    imagem_fundo = pygame.image.load('assets/background-day.png')
    imagem_fundo = pygame.transform.scale(imagem_fundo, (LARGURA_TELA, ALTURA_TELA))

    # Cria um grupo de sprites para o personagem e adiciona o personagem ao grupo
    grupo_caramelo = pygame.sprite.Group()
    caramelo = Caramelo()
    grupo_caramelo.add(caramelo)

    # Cria um grupo de sprites para o chão e adiciona o chão ao grupo
    grupo_chao = pygame.sprite.Group()
    for i in range(2):
        chao = Chao(LARGURA_CHAO * i)
        grupo_chao.add(chao)

    # Cria um grupo de sprites para os tubos e adiciona os tubos ao grupo
    grupo_tubos = pygame.sprite.Group()
    for i in range(2):
        tubo = criar_tubo_aleatorio(LARGURA_TELA * i + 800)
        grupo_tubos.add(tubo[0])
        grupo_tubos.add(tubo[1])

    # Cria um relógio para controlar a taxa de atualização do jogo
    clock = pygame.time.Clock()

    # Loop principal do jogo
    while True:

        clock.tick(30)  # Define a taxa de quadros por segundo (FPS)

        # Processa os eventos do jogo
        for evento in pygame.event.get():
            # Verifica se o evento é QUIT e, em caso afirmativo, encerra o jogo
            if evento.type == QUIT:
                pygame.quit()

            # Verifica se uma tecla foi pressionada
            if evento.type == KEYDOWN:
                # Se a tecla pressionada for a barra de espaço, faz o personagem pular
                if evento.key == K_SPACE:
                    caramelo.pular()

        # Desenha a imagem de fundo na tela
        tela.blit(imagem_fundo, (0, 0))

        # Verifica se o chão saiu da tela
        if esta_fora_da_tela(grupo_chao.sprites()[0]):
            # Remove o chão do grupo
            grupo_chao.remove(grupo_chao.sprites()[0])
            # Cria um novo chão e adiciona ao grupo
            novo_chao = Chao(LARGURA_TELA - 20)
            grupo_chao.add(novo_chao)

        # Verifica se o tubo saiu da tela
        if esta_fora_da_tela(grupo_tubos.sprites()[0]):
            # Remove o tubo do grupo
            grupo_tubos.remove(grupo_tubos.sprites()[0])
            grupo_tubos.remove(grupo_tubos.sprites()[0])
            # Cria um novo tubo e adiciona ao grupo
            tubo = criar_tubo_aleatorio(2 * LARGURA_TELA)
            grupo_tubos.add(tubo[0])
            grupo_tubos.add(tubo[1])

        # Atualiza: o estado do personagem, o chão e os tubos
        grupo_caramelo.update()
        grupo_chao.update()
        grupo_tubos.update()

        # Desenha: o personagem, o chão e os tubos na tela
        grupo_caramelo.draw(tela)
        grupo_tubos.draw(tela)
        grupo_chao.draw(tela)

        # Atualiza a tela com o que foi desenhado
        pygame.display.update()

        # Verifica se houve colisão entre o personagem e o chão
        if (pygame.sprite.groupcollide(grupo_caramelo, grupo_chao, False, False, pygame.sprite.collide_mask) or
                pygame.sprite.groupcollide(grupo_caramelo, grupo_tubos, False, False, pygame.sprite.collide_mask)):
            input()
            break


# Chama a função principal
if __name__ == '__main__':
    main()
