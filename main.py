import pygame
from pygame.locals import *

LARGURA_TELA = 400
ALTURA_TELA = 800
VELOCIDADE = 10
GRAVIDADE = 1

class Caramelo(pygame.sprite.Sprite):

  def __init__(self):
    pygame.sprite.Sprite.__init__(self)

    self.imagens = [pygame.image.load('assets/bluebird-midflap.png').convert_alpha(),
                   pygame.image.load('assets/bluebird-upflap.png').convert_alpha(),
                   pygame.image.load('assets/bluebird-downflap.png').convert_alpha()]
    
    # Sipa consta arrumar essa gambiarra
    self.velocidade = VELOCIDADE

    self.imagem_atual = 0

    self.image = pygame.image.load('assets/bluebird-upflap.png').convert_alpha()

    self.rect = self.image.get_rect()
    # Centralizando o cachorro caramelo
    self.rect[0] = LARGURA_TELA / 2
    self.rect[1] = ALTURA_TELA / 2

  def update(self):
    self.imagem_atual = (self.imagem_atual + 1) % 3
    self.image = self.imagens[self.imagem_atual]

    self.velocidade += GRAVIDADE

    # Mudando a altura
    self.rect[1] += self.velocidade

  def pular(self):
    self.velocidade = -VELOCIDADE

pygame.init()
tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))

imagemFundo = pygame.image.load('assets/background-day.png')
fundo = pygame.transform.scale(imagemFundo, (LARGURA_TELA, ALTURA_TELA))

grupo_caramelo = pygame.sprite.Group()
caramelo = Caramelo()
grupo_caramelo.add(caramelo)

# Controlando o FPS
clock = pygame.time.Clock()

while True:
  # Frames Por Segundo
  clock.tick(20)

  for evento in pygame.event.get():
    if evento.type == QUIT:
      pygame.quit()

    # Tecla Para Pular
    if evento.type == KEYDOWN:
      if evento.key == K_SPACE:
        caramelo.pular()

  tela.blit(fundo, (0, 0))

  grupo_caramelo.update()

  grupo_caramelo.draw(tela)

  pygame.display.update()
