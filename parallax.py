import pygame
import math
from common import SpriteCounter


class PlanePanel(pygame.sprite.Sprite):
    containers = []
    def __init__(self, image, rect):
        pygame.sprite.DirtySprite.__init__(self, self.containers)
        self.image = image
        self.rect = rect


class Plane(pygame.sprite.RenderUpdates):

    def __init__(self, image, rect, *containers):
        pygame.sprite.RenderUpdates.__init__(self)
        self.image = image
        self.rect = rect
        self.offset = 0

        self.panels = {}

        for i in range(0, math.ceil(self.rect.width/self.image.get_width()) + 1):
            panel = PlanePanel(self.image, pygame.Rect((self.rect.left + i*self.image.get_width(), self.rect.top), self.image.get_size()))
            self.panels[i] = panel
            self.add(panel)

        for x in containers:
            containers.add(self)

    def set_offset(self, offset):
        self.offset = offset % self.image.get_width()
        for i, panel in self.panels.items():
            panel.rect = pygame.Rect((self.offset + self.rect.left + (i-1)*self.image.get_width(), self.rect.top), self.image.get_size())
            panel.dirty = 1


def main():
    pygame.init()
    screen_rect = pygame.Rect((0, 0, 800, 600))
    screen = pygame.display.set_mode(screen_rect.size)
    background = pygame.Surface(screen_rect.size)
    background.fill((0, 0, 0))

    hills_back = pygame.image.load("hills_back.png").convert_alpha()
    hills_mid = pygame.image.load("hills_mid.png").convert_alpha()
    hills_front = pygame.image.load("hills_front.png").convert_alpha()


    counter = SpriteCounter()

    plane1 = Plane(hills_back, screen_rect)
    plane2 = Plane(hills_mid, screen_rect)
    plane3 = Plane(hills_front, screen_rect)


    autoscroll = True
    
    while 1:
        if pygame.event.peek(pygame.QUIT):
            pygame.quit()
            raise SystemExit()

        if pygame.key.get_pressed()[pygame.K_d] or autoscroll:
            plane1.set_offset(plane1.offset + 0.25)
            plane2.set_offset(plane2.offset + 0.5)
            plane3.set_offset(plane3.offset + 1)
        elif pygame.key.get_pressed()[pygame.K_a]:
            plane1.set_offset(plane1.offset - 0.25)
            plane2.set_offset(plane2.offset - 0.5)
            plane3.set_offset(plane3.offset - 1)
        # for event in pygame.event.get(pygame.KEYDOWN):
        #     if event.unicode == "d":
        #         plane1.set_offset(plane1.offset + 1)

        pygame.event.clear()

        screen.fill(pygame.Color("#7ec0ee"))
        for plane in [plane1, plane2, plane3]:
            # plane.clear(screen, background)
            plane.update()
            plane.draw(screen)

        counter.update()
        screen.blit(counter.image, counter.rect)

        pygame.display.flip()


if __name__ == "__main__":
    main()
