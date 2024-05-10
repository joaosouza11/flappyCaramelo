# Bibliotecas padrão
import random
from typing import Tuple

# Bibliotecas de terceiros
import pygame
from pygame import display, Surface, sprite, SRCALPHA, event
from pygame._sprite import collide_mask
from pygame.display import set_mode
from pygame.font import Font, SysFont
from pygame.image import load
from pygame.locals import (QUIT, KEYDOWN, K_SPACE)
from pygame.mask import from_surface
from pygame.sprite import Group, GroupSingle, Sprite, groupcollide
from pygame.time import Clock
from pygame.transform import scale, flip

# Largura e altura da tela
LARGURA_TELA = 390
ALTURA_TELA = 844

# Largura e altura do chão
LARGURA_CHAO = 2 * LARGURA_TELA
ALTURA_CHAO = 100

# Largura, Altura e intervalo entre os tubos
LARGURA_TUBO = 120
ALTURA_TUBO = 500
INTERVALO_TUBO = 200

# Define a velocidade inicial e a gravidade que afeta o personagem
VELOCIDADE = 10
GRAVIDADE = 1

# Define a velocidade do jogo
VELOCIDADE_JOGO = 8

tela = set_mode((LARGURA_TELA, ALTURA_TELA))


# Define a classe do passaro Caramelo, que herda de pygame.sprite.Sprite
class Caramelo(Sprite):

    # Método constructor da classe
    def __init__(self):
        Sprite.__init__(self)

        # Carrega as imagens do personagem e as armazena em uma lista
        self.imagens = [load('assets/CarameloMid.png').convert_alpha(),
                        load('assets/CarameloUp.png').convert_alpha(),
                        load('assets/CarameloDown.png').convert_alpha()]

        # Define a velocidade do personagem como a velocidade inicial
        self.velocidade = VELOCIDADE

        # Inicializa o índice da imagem atual do personagem, define a imagem inicial do personagem
        # e ajusta a máscara de colisão
        self.imagem_atual = 0
        self.image = load('assets/CarameloUp.png').convert_alpha()
        self.mask = from_surface(self.image)

        # Cria um retângulo para a imagem, que será usado para a posição e colisões
        self.rect = self.image.get_rect()
        self.rect[0] = LARGURA_TELA / 2
        self.rect[1] = ALTURA_TELA / 2

    # Método para atualizar o estado do personagem
    def update(self) -> None:
        # Atualiza o índice da imagem para animar o personagem
        self.imagem_atual = (self.imagem_atual + 1) % 3
        self.image = self.imagens[self.imagem_atual]

        # Aplica a gravidade à velocidade do personagem
        self.velocidade += GRAVIDADE

        # Atualiza a posição vertical do personagem com base na velocidade
        self.rect[1] += self.velocidade

    def pular(self) -> None:
        # Inverte a velocidade para friar um movimento de pulo
        self.velocidade = -VELOCIDADE


# Define a classe Tubo, que herda de pygame.sprite.Sprite
class Tubo(Sprite):
    def __init__(self, xpos, ysize, inverted):
        Sprite.__init__(self)

        # Carrega a imagem do tubo e a ajusta para preencher a tela
        self.image = load('assets/chinelo.png')
        self.image = scale(self.image, (LARGURA_TUBO, ALTURA_TUBO))

        # Cria um retângulo para a imagem, que será usado para a posição e colisões
        self.rect = self.image.get_rect()
        self.rect[0] = xpos

        # Posiciona o tubo na parte superior ou inferior da tela
        if inverted:
            self.image = flip(self.image, False, True)
            self.rect[1] = - (self.rect[3] - ysize)
        else:
            self.rect[1] = ALTURA_TELA - ysize

        # Cria uma máscara para a imagem, que será usada para colisões
        self.mask = from_surface(self.image)

    def update(self) -> None:
        self.rect[0] -= VELOCIDADE_JOGO


# Classe Chao herda de pygame.sprite.Sprite
class Chao(Sprite):
    def __init__(self, xpos):
        Sprite.__init__(self)

        # Carrega a imagem do chão e a ajusta para preencher a tela
        self.image = load('assets/base.png')
        self.image = scale(self.image, (LARGURA_CHAO, ALTURA_CHAO))

        # Cria um retângulo para a imagem, que será usado para a posição e
        # colisões e Posiciona na parte inferior da tela
        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        self.rect[1] = ALTURA_TELA - ALTURA_CHAO

    # Método para atualizar o estado do chão
    def update(self) -> None:
        # Move o chão para a esquerda para criar a ilusão de movimento do personagem
        self.rect[0] -= VELOCIDADE_JOGO


# Classe Botao herda de pygame.sprite.Sprite
class Botao(Sprite):
    def __init__(self, x, y):

        Sprite.__init__(self)

        self.image = load('assets/restart.png')
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def clique(self):

        acao = False

        # Pegando a posição do mouse
        pos = pygame.mouse.get_pos()

        # Checa se o mouse está em cima do botao
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                acao = True

        tela.blit(self.image, (self.rect.x, self.rect.y))

        return acao


# Função para verificar se um sprite saiu da tela
def esta_fora_da_tela(sprite: Tubo) -> bool:
    """Verifica se um sprite saiu da tela pela esquerda."""
    return sprite.rect[0] < -sprite.rect[2]


def criar_tubo_aleatorio(xpos: int) -> Tuple[Tubo, Tubo]:
    """Cria um par de tubos (superior e inferior) com uma abertura aleatória."""
    tamanho = random.randint(100, 300)
    tubo = Tubo(xpos, tamanho, False)
    tubo_invertido = Tubo(xpos, ALTURA_TELA - tamanho - INTERVALO_TUBO, True)
    return tubo, tubo_invertido


def inicializar_jogo() -> Tuple[Surface, Surface]:
    """Inicializa o Pygame, cria a tela e carrega os recursos."""
    pygame.init()
    tela = set_mode((LARGURA_TELA, ALTURA_TELA))
    imagem_fundo = load('assets/background-brasil.png').convert()
    imagem_fundo = scale(imagem_fundo, (LARGURA_TELA, ALTURA_TELA))
    return tela, imagem_fundo


def criar_sprites() -> Tuple[GroupSingle, Group, Group]:
    """Cria os grupos de sprites e adiciona os elementos iniciais."""
    grupo_caramelo = GroupSingle(Caramelo())
    grupo_chao = sprite.Group()
    for i in range(2):
        chao = Chao(LARGURA_CHAO * i)
        grupo_chao.add(chao)
    grupo_tubos = Group()
    for i in range(2):
        tubos = criar_tubo_aleatorio(LARGURA_TELA * i + 800)
        grupo_tubos.add(tubos[0])
        grupo_tubos.add(tubos[1])
    return grupo_caramelo, grupo_chao, grupo_tubos


def processar_eventos(caramelo: Caramelo) -> None:
    """Processa os eventos do jogo, como pressionamento de teclas."""
    for evento in event.get():
        if evento.type == QUIT:
            pygame.quit()
            exit()
        if evento.type == KEYDOWN:
            if evento.key == K_SPACE:
                caramelo.pular()


def atualizar_elementos_jogo(grupo_caramelo: GroupSingle, grupo_chao: Group, grupo_tubos: Group) -> None:
    """Atualiza a posição e o estado dos elementos do jogo."""
    grupo_caramelo.update()
    grupo_chao.update()
    grupo_tubos.update()

    if esta_fora_da_tela(grupo_chao.sprites()[0]):
        grupo_chao.remove(grupo_chao.sprites()[0])
        novo_chao = Chao(LARGURA_CHAO - 20)
        grupo_chao.add(novo_chao)

    if esta_fora_da_tela(grupo_tubos.sprites()[0]):
        grupo_tubos.remove(grupo_tubos.sprites()[0])
        grupo_tubos.remove(grupo_tubos.sprites()[0])
        novos_tubos = criar_tubo_aleatorio(LARGURA_TELA * 2)
        grupo_tubos.add(novos_tubos[0])
        grupo_tubos.add(novos_tubos[1])


def desenhar_elementos_jogo(tela: Surface,
                            imagem_fundo: Surface,
                            grupo_caramelo: GroupSingle,
                            grupo_chao: Group,
                            grupo_tubos: Group) -> None:
    """Desenha os elementos do jogo na tela."""
    tela.blit(imagem_fundo, (0, 0))
    grupo_caramelo.draw(tela)
    grupo_tubos.draw(tela)
    grupo_chao.draw(tela)
    display.update()


def verificar_colisoes(grupo_caramelo: GroupSingle, grupo_chao: Group, grupo_tubos: Group) -> bool:
    """Verifica se houve colisões entre o caramelo e outros elementos."""
    colisao_chao = groupcollide(grupo_caramelo, grupo_chao, False, False, collide_mask)
    colisao_tubo = groupcollide(grupo_caramelo, grupo_tubos, False, False, collide_mask)
    if colisao_chao or colisao_tubo:
        return True


def desenha_pontos(texto: str, fonte: Font, cor_texto: Tuple[int, int, int], x: int, y: int) -> None:
    img = fonte.render(texto, True, cor_texto)
    tela.blit(img, (x, y))


# Restarta o jogo quando clicar no botão
def restarta_jogo() -> None:
    global surface_placar

    pontuacao = 0
    passou_tubo = False
    grupo_caramelo, grupo_chao, grupo_tubos = criar_sprites()

    # Recria a superfície do placar
    surface_placar.fill((0, 0, 0))


botao = Botao(LARGURA_TELA // 2 - 50, ALTURA_TELA // 2 + 12)


def tela_inicio(tela: Surface, imagem_fundo: Surface) -> None:
    """Exibe uma tela de início simples."""
    fonte = SysFont('Bauhaus 93', 27)
    texto = fonte.render('Pressione Espaço para Iniciar', True, (255, 255, 255))
    while True:
        for evento in pygame.event.get():
            if evento.type == QUIT:
                pygame.quit()
                exit()
            if evento.type == KEYDOWN:
                if evento.key == K_SPACE:
                    return  # Sai da tela de início

        tela.blit(imagem_fundo, (0, 0))
        tela.blit(texto, (LARGURA_TELA // 2 - texto.get_width() // 2, ALTURA_TELA // 2))
        pygame.display.flip()


def main():
    """Função principal do jogo."""
    tela, imagem_fundo = inicializar_jogo()
    grupo_caramelo, grupo_chao, grupo_tubos = criar_sprites()
    clock = Clock()

    # Exibe a tela de início
    tela_inicio(tela, imagem_fundo)

    # Declarando pontuação inicial e se passou do tubo
    pontuacao = 0
    passou_tubo = False

    # Criando a superfície para o placar
    fonte_placar = SysFont('Bauhaus 93', 60)
    surface_placar = Surface((LARGURA_TELA, fonte_placar.get_height()), SRCALPHA)

    # Variáveis para controlar o estado do jogo
    game_over = False
    rodando = True

    while rodando:
        clock.tick(30)

        # Conta a pontuação do jogo
        if len(grupo_tubos) > 0:
            if grupo_caramelo.sprites()[0].rect.left > grupo_tubos.sprites()[0].rect.left \
                    and grupo_caramelo.sprites()[0].rect.right < grupo_tubos.sprites()[0].rect.right \
                    and passou_tubo == False:
                passou_tubo = True
        if passou_tubo:
            if grupo_caramelo.sprites()[0].rect.left > grupo_tubos.sprites()[0].rect.right:
                pontuacao += 1
                passou_tubo = False

        if verificar_colisoes(grupo_caramelo, grupo_chao, grupo_tubos):
            game_over = True

        if not game_over:
            processar_eventos(grupo_caramelo.sprite)
            atualizar_elementos_jogo(grupo_caramelo, grupo_chao, grupo_tubos)

            # Atualiza o placar
            texto_placar = fonte_placar.render(str(pontuacao), True, (255, 255, 255, 128))  # Adiciona alpha ao texto
            largura_texto = texto_placar.get_width()
            rect_placar = texto_placar.get_rect(center=(LARGURA_TELA // 2, surface_placar.get_height() // 2))

            # Cria um retângulo menor para apagar apenas o texto antigo
            rect_apagar = pygame.Rect(rect_placar.left - 180, rect_placar.top, largura_texto + 380, rect_placar.height)
            surface_placar.fill((0, 0, 0, 0), rect_apagar)  # Preenche com transparência
            surface_placar.blit(texto_placar, rect_placar)

            desenhar_elementos_jogo(tela, imagem_fundo, grupo_caramelo, grupo_chao, grupo_tubos)
            tela.blit(surface_placar, (0, 20))

            # Atualiza apenas a área do placar
            area_placar = surface_placar.get_rect(topleft=(0, 20))
            pygame.display.update(area_placar)
        else:
            # Game Over: Exibe mensagem, pontuação e botão de reiniciar
            fonte_gameover = SysFont('Bauhaus 93', 40)
            texto_gameover = fonte_gameover.render('Game Over', True, (255, 0, 0))
            texto_pontuacao = fonte_gameover.render(f'Pontuação: {pontuacao}', True, (255, 255, 255))
            tela.blit(imagem_fundo, (0, 0))
            tela.blit(texto_gameover, (LARGURA_TELA // 2 - texto_gameover.get_width() // 2, ALTURA_TELA // 2 - 80))
            tela.blit(texto_pontuacao, (LARGURA_TELA // 2 - texto_pontuacao.get_width() // 2, ALTURA_TELA // 2 - 40))

            for evento in event.get():
                if evento.type == QUIT:
                    rodando = False
                elif evento.type == KEYDOWN:
                    if evento.key == K_SPACE:
                        # Reinicia o jogo se a tecla Espaço for pressionada
                        pontuacao = 0
                        passou_tubo = False
                        game_over = False
                        grupo_caramelo, grupo_chao, grupo_tubos = criar_sprites()

            if botao.clique():
                # Reinicia o jogo se o botão for clicado
                pontuacao = 0
                passou_tubo = False
                game_over = False
                grupo_caramelo, grupo_chao, grupo_tubos = criar_sprites()

        display.flip()

    quit()


# Chama a função principal
if __name__ == '__main__':
    main()
