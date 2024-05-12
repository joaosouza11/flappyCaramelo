import random
from typing import Tuple

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
LARGURA_TELA = 550
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
GRAVIDADE = 0.8

# Define a velocidade do jogo
VELOCIDADE_JOGO = 9

# Inicializa o Pygame
pygame.init()

# Define a tela do jogo
tela = set_mode((LARGURA_TELA, ALTURA_TELA))


# --- Classes ---
class Caramelo(Sprite):
    """Classe do pássaro Caramelo."""

    def __init__(self):
        """Inicializa o Caramelo."""
        super().__init__()
        self.imagens = [
            load('assets/CarameloMid.png').convert_alpha(),
            load('assets/CarameloUp.png').convert_alpha(),
            load('assets/CarameloDown.png').convert_alpha()
        ]
        self.velocidade = VELOCIDADE
        self.imagem_atual = 0
        self.image = load('assets/CarameloUp.png').convert_alpha()
        self.mask = from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect[0] = LARGURA_TELA / 4
        self.rect[1] = ALTURA_TELA / 2

    def update(self) -> None:
        """Atualiza o estado do Caramelo."""
        self.imagem_atual = (self.imagem_atual + 1) % 3
        self.image = self.imagens[self.imagem_atual]
        self.velocidade += GRAVIDADE
        self.rect[1] += self.velocidade

    def pular(self) -> None:
        """Faz o Caramelo pular."""
        self.velocidade = -VELOCIDADE


class Tubo(Sprite):
    """Classe que representa um tubo."""

    def __init__(self, xpos: int, ysize: int, inverted: bool):
        """Inicializa o Tubo."""
        super().__init__()
        self.image = load('assets/chinelo.png')
        self.image = scale(self.image, (LARGURA_TUBO, ALTURA_TUBO))
        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        if inverted:
            self.image = flip(self.image, False, True)
            self.rect[1] = -(self.rect[3] - ysize)
        else:
            self.rect[1] = ALTURA_TELA - ysize
        self.mask = from_surface(self.image)

    def update(self) -> None:
        """Atualiza a posição do Tubo."""
        self.rect[0] -= VELOCIDADE_JOGO


class Chao(Sprite):
    """Classe que representa o chão."""

    def __init__(self, xpos: int):
        """Inicializa o Chao."""
        super().__init__()
        self.image = load('assets/base.png')
        self.image = scale(self.image, (LARGURA_CHAO, ALTURA_CHAO))
        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        self.rect[1] = ALTURA_TELA - ALTURA_CHAO

    def update(self) -> None:
        """Atualiza a posição do Chao."""
        self.rect[0] -= VELOCIDADE_JOGO


class Botao(Sprite):
    """Classe que representa o botão de reiniciar."""

    def __init__(self, x: int, y: int):
        """Inicializa o Botao."""
        super().__init__()
        self.image = load('assets/restart.png')
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def clique(self) -> bool:
        """Verifica se o botão foi clicado."""
        acao = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                acao = True
        tela.blit(self.image, (self.rect.x, self.rect.y))
        return acao


# --- Funções ---
def esta_fora_da_tela(sprite: Tubo) -> bool:
    """Verifica se um sprite saiu da tela pela esquerda."""
    return sprite.rect[0] < -sprite.rect[2]


def criar_tubo_aleatorio(xpos: int) -> Tuple[Tubo, Tubo]:
    """Cria um par de tubos (superior e inferior) com uma abertura aleatória."""
    tamanho = random.randint(200, 550)
    tubo = Tubo(xpos, tamanho, False)
    tubo_invertido = Tubo(xpos, ALTURA_TELA - tamanho - INTERVALO_TUBO, True)
    return tubo, tubo_invertido


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


def atualizar_elementos_jogo(grupo_caramelo: GroupSingle,
                             grupo_chao: Group,
                             grupo_tubos: Group) -> None:
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


def verificar_colisoes(grupo_caramelo: GroupSingle,
                       grupo_chao: Group,
                       grupo_tubos: Group) -> bool:
    """Verifica se houve colisões entre o caramelo e outros elementos."""
    colisao_chao = groupcollide(grupo_caramelo, grupo_chao, False, False,
                                collide_mask)
    colisao_tubo = groupcollide(grupo_caramelo, grupo_tubos, False, False,
                                collide_mask)
    return colisao_chao or colisao_tubo


def desenha_pontos(texto: str,
                   fonte: Font,
                   cor_texto: Tuple[int, int, int],
                   x: int,
                   y: int) -> None:
    """Desenha a pontuação na tela."""
    img = fonte.render(texto, True, cor_texto)
    tela.blit(img, (x, y))


def inicializar_jogo() -> Tuple[Surface, Surface]:
    """Inicializa o jogo e carrega os recursos."""
    tela = set_mode((LARGURA_TELA, ALTURA_TELA))
    imagem_fundo = load('assets/background-brasil.png').convert()
    imagem_fundo = scale(imagem_fundo, (LARGURA_TELA, ALTURA_TELA))
    return tela, imagem_fundo


def tela_inicio(tela: Surface, imagem_fundo: Surface) -> None:
    """Exibe a tela de início do jogo."""
    fonte = SysFont('Bauhaus 93', 27)
    texto = fonte.render('Pressione Espaço para Iniciar', True,
                         (255, 255, 255))

    while True:
        for evento in pygame.event.get():
            if evento.type == QUIT:
                pygame.quit()
                exit()
            if evento.type == KEYDOWN:
                if evento.key == K_SPACE:
                    return

        tela.blit(imagem_fundo, (0, 0))
        tela.blit(texto, (LARGURA_TELA // 2 - texto.get_width() // 2,
                          ALTURA_TELA // 2))
        pygame.display.flip()


def carregar_recorde() -> int:
    """Carrega o recorde do arquivo, se existir."""
    try:
        with open('recorde.txt', 'r') as arquivo:
            return int(arquivo.read())
    except FileNotFoundError:
        return 0


def salvar_recorde(recorde: int) -> None:
    """Salva o recorde no arquivo."""
    with open('recorde.txt', 'w') as arquivo:
        arquivo.write(str(recorde))


def jogar(tela: Surface, imagem_fundo: Surface) -> None:
    """Contém a lógica principal do jogo."""
    grupo_caramelo, grupo_chao, grupo_tubos = criar_sprites()
    clock = Clock()

    pontuacao = 0

    # Carrega o recorde
    maior_pontuacao = carregar_recorde()

    passou_tubo = False
    fonte_placar = SysFont('Bauhaus 93', 60)
    surface_placar = Surface((LARGURA_TELA, fonte_placar.get_height()),
                             SRCALPHA)
    botao = Botao(LARGURA_TELA / 2 - 60, ALTURA_TELA // 2 + 12)

    game_over = False

    while True:
        clock.tick(30)

        # Verifica a pontuação
        if len(grupo_tubos) > 0:
            if (grupo_caramelo.sprites()[0].rect.left >
                    grupo_tubos.sprites()[0].rect.left and
                    grupo_caramelo.sprites()[0].rect.right <
                    grupo_tubos.sprites()[0].rect.right and
                    not passou_tubo):
                passou_tubo = True
        if passou_tubo:
            if grupo_caramelo.sprites()[0].rect.left > grupo_tubos.sprites()[
                0].rect.right:
                pontuacao += 1
                passou_tubo = False

        if verificar_colisoes(grupo_caramelo, grupo_chao, grupo_tubos):
            game_over = True

        if not game_over:
            processar_eventos(grupo_caramelo.sprite)
            atualizar_elementos_jogo(grupo_caramelo, grupo_chao, grupo_tubos)

            # Atualiza o placar
            texto_placar = fonte_placar.render(str(pontuacao), True,
                                               (255, 255, 255, 128))
            largura_texto = texto_placar.get_width()
            rect_placar = texto_placar.get_rect(
                center=(LARGURA_TELA // 2, surface_placar.get_height() // 2))

            # Apaga o texto antigo do placar
            rect_apagar = pygame.Rect(rect_placar.left - 180,
                                      rect_placar.top, largura_texto + 380,
                                      rect_placar.height)
            surface_placar.fill((0, 0, 0, 0), rect_apagar)

            surface_placar.blit(texto_placar, rect_placar)
            desenhar_elementos_jogo(tela, imagem_fundo, grupo_caramelo,
                                    grupo_chao, grupo_tubos)
            tela.blit(surface_placar, (0, 20))

            # Atualiza apenas a área do placar
            area_placar = surface_placar.get_rect(topleft=(0, 20))
            pygame.display.update(area_placar)

        else:
            # Verifica a maior pontuação
            if pontuacao > maior_pontuacao:
                maior_pontuacao = pontuacao
                salvar_recorde(maior_pontuacao)

            # Exibe a tela de Game Over
            fonte_gameover = SysFont('Bauhaus 93', 40)
            fonte_pontuacao = SysFont('Bauhaus 93', 30)
            texto_gameover = fonte_gameover.render('Game Over', True,
                                                   (255, 0, 0))
            texto_recorde = fonte_pontuacao.render(
                f'Recorde: {maior_pontuacao}', True, (255, 255, 255))
            texto_pontuacao = fonte_pontuacao.render(
                f'Sua Pontuação: {pontuacao}', True, (255, 255, 255))
            tela.blit(imagem_fundo, (0, 0))
            tela.blit(texto_gameover, (LARGURA_TELA // 2 -
                                       texto_gameover.get_width() // 2,
                                       ALTURA_TELA // 2 - 120))
            tela.blit(texto_recorde, (LARGURA_TELA // 2 -
                                      texto_recorde.get_width() // 2,
                                      ALTURA_TELA // 2 - 70))
            tela.blit(texto_pontuacao, (LARGURA_TELA // 2 -
                                        texto_pontuacao.get_width() // 2,
                                        ALTURA_TELA // 2 - 35))

            for evento in event.get():
                if evento.type == QUIT:
                    pygame.quit()
                    exit()
                elif evento.type == KEYDOWN:
                    if evento.key == K_SPACE:
                        # Reinicia o jogo se 'Espaço' for pressionado
                        return jogar(tela, imagem_fundo)
            if botao.clique():
                # Reinicia o jogo se o botão for clicado
                return jogar(tela, imagem_fundo)

        display.flip()


def main():
    """Função principal do jogo."""
    tela, imagem_fundo = inicializar_jogo()
    tela_inicio(tela, imagem_fundo)
    jogar(tela, imagem_fundo)
    pygame.quit()


if __name__ == '__main__':
    main()
