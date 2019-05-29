"""Menu screen."""
import pygame
from . import params
from . import assets
from . import gui
from .simulation import Simulation

key_to_function = {
    # insert lambda hooks here
}


class Menu:
    """The menu loop."""

    def __init__(self):
        self.running = True
        self.screen = pygame.display.set_mode(params.SCREEN_SIZE)
        pygame.display.set_icon(assets.image('boids-logo.png'))
        pygame.display.set_caption(params.CAPTION)
        self.clock = pygame.time.Clock()
        self.to_update = pygame.sprite.Group()
        self.to_display = pygame.sprite.Group()

    def update(self, motion_event, click_event):
        self.to_update.update(motion_event, click_event)

    def display(self):
        for sprite in self.to_display:
            sprite.display(self.screen)

    def start_simulation(self):
        s = Simulation(self.screen)
        if s.run() == "PYGAME_QUIT":
            self.quit()

    def main(self):
        self.to_update = pygame.sprite.Group(
            gui.Button(
                pos=(6, 5.5), text="Start", font=params.H3_FONT,
                action=lambda: self.start_simulation()),
            gui.Button(
                pos=(6, 8), text="Quit", font=params.H3_FONT,
                action=lambda: self.quit())
        )
        self.to_display = pygame.sprite.Group(
            self.to_update,
            gui.Message(pos=(6, 2), text="PyBoids", font=params.H1_FONT),
            gui.Message(
                pos=(6, 3), text="An implementation of steering behaviors.",
                font=params.H5_FONT),
        )
        texts = []
        texts.append(
            "There are three entities : Boid - Leader boid - Obstacle.")
        texts.append("Right click to add an entity to the simulation space.")
        texts.append(
            "You can play with many different behaviors by toggling" +
            "them on or off.")
        texts.append("Have fun !")
        self.to_display.add(
            gui.Message(pos=(6, 3.3 + 0.3 * k), text=t)
            for k, t in enumerate(texts))

        while self.running:
            motion_event, click_event = None, None
            self.screen.fill(params.MENU_BACKGROUND)
            self.clock.tick(params.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in key_to_function:
                        key_to_function[event.key](self, event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    click_event = event
                elif event.type == pygame.MOUSEMOTION:
                    motion_event = event
            self.update(motion_event, click_event)
            self.display()
            pygame.display.flip()
        pygame.quit()

    def quit(self):
        self.running = False
