import pygame
import os
from scenes.scene import Scene
from config import config
from gui import Label, RectButton, create_rect_surface
from constants import Colors, Fonts


class SettingsMenu(Scene):
    def __init__(self):
        super().__init__()
        self.volume_bar = VolumeBar()
        self.sub_menu = None
        self.piece_assets_menu = PieceAssetsMenu()
        self.board_assets_menu = BoardAssetsMenu()
        self.filter = create_rect_surface(Colors.BLACK, config.width, config.height, 0, 150)

    def create_buttons(self):
        self.buttons = {
            "piece": RectButton(config.width*0.2, config.height*0.2, config.width*0.3, config.height*0.1, 0, Colors.WHITE, 'piece assets', Fonts.GEIZER, Colors.BLACK, lambda:self.change_sub_menu('piece')),
            "board": RectButton(config.width*0.2, config.height*0.3, config.width*0.3, config.height*0.1, 0, Colors.WHITE, 'board assets', Fonts.GEIZER, Colors.BLACK, lambda:self.change_sub_menu('board'))
        }

    def change_sub_menu(self, menu):
        self.sub_menu = menu
    
    def render(self, screen):
        screen.fill(Colors.BLACK.value)
        super().render(screen)
        self.volume_bar.draw(screen)
        if self.sub_menu == 'piece':
            screen.blit(self.filter)
            self.piece_assets_menu.render(screen)
        elif self.sub_menu == 'board':
            screen.blit(self.filter)
            self.board_assets_menu.render(screen)

    def update(self):
        if not self.sub_menu:
            super().update()
            self.volume_bar.update()
        elif self.sub_menu == 'piece':
            self.piece_assets_menu.update()
        elif self.sub_menu == 'board':
            self.board_assets_menu.update()

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        if not self.sub_menu:
            super().handle_event(event)
        elif self.sub_menu == 'piece':
            self.piece_assets_menu.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:           
                if mouse_pos[0] < list(self.piece_assets_menu.buttons.values())[0].rect.left or mouse_pos[0] > list(self.piece_assets_menu.buttons.values())[0].rect.right:
                    self.change_sub_menu(None)
        elif self.sub_menu == 'board':
            self.board_assets_menu.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if mouse_pos[0] < list(self.board_assets_menu.buttons.values())[0].rect.left or mouse_pos[0] > list(self.board_assets_menu.buttons.values())[0].rect.right:
                    self.change_sub_menu(None)
        
class VolumeBar:
    def __init__(self):
        self.rect = pygame.Rect(config.width * 0.5, config.height * 0.5, config.width * 0.2, config.height * 0.07)
        self.circle_pos = [self.rect.x + self.rect.width * config.volume, self.rect.centery]
        self.circle_radius = self.rect.height * 0.5
        self.line_start = (self.rect.x, self.rect.y + self.rect.height // 2)
        self.line_end = (self.rect.x + self.rect.width, self.rect.y + self.rect.height // 2)

    def draw(self, screen):
        pygame.draw.line(screen, Colors.WHITE.value, self.line_start, self.line_end, self.rect.height // 4)
        pygame.draw.circle(screen, Colors.WHITE.value, self.circle_pos, self.circle_radius)

    def update(self):
        if pygame.mouse.get_pressed()[0]:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                self.circle_pos[0] = mouse_pos[0]
                config.volume = (mouse_pos[0] - self.rect.x) / self.rect.width
                print(config.volume)

class PieceAssetsMenu(Scene):
    def __init__(self):
        super().__init__()

    def create_buttons(self):
        self.buttons = {asset: RectButton(config.width*0.5, config.height*0.05+(config.height*0.1*i), config.width*0.5, config.height*0.1, 0, Colors.WHITE, asset, Fonts.GEIZER, Colors.BLACK, lambda:None) for i, asset in enumerate(os.listdir('assets/piece'))}

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for asset, button in self.buttons.items():
                    if button.is_clicked():
                        self.change_asset(asset)
            elif event.button == 4 and list(self.buttons.values())[0].rect.top < 0 :
                for button in self.buttons.values():
                    button.y += 10
                    button.rect.y += 10
                    button.label.rect.y += 10
            elif event.button == 5 and list(self.buttons.values())[len(self.buttons)-1].rect.bottom > config.height:
                for button in self.buttons.values():
                    button.y -= 10
                    button.rect.y -= 10
                    button.label.rect.y -= 10    

    def change_asset(self, asset):
        self.buttons[config.piece_asset].update_color(Colors.WHITE)
        config.piece_asset = asset
        self.buttons[asset].update_color(Colors.GREEN)

class BoardAssetsMenu(Scene):
    def __init__(self):
        super().__init__()

    def create_buttons(self):
        self.buttons = {os.path.splitext(asset)[0]: RectButton(config.width*0.5, config.height*0.05+(config.height*0.1*i), config.width*0.5, config.height*0.1, 0, Colors.WHITE, os.path.splitext(asset)[0], Fonts.GEIZER, Colors.BLACK, lambda:None) for i, asset in enumerate(os.listdir('assets/board'))}

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for asset, button in self.buttons.items():
                    if button.is_clicked():
                        self.change_asset(asset)
            elif event.button == 4 and list(self.buttons.values())[0].rect.top < 0 :
                for button in self.buttons.values():
                    button.y += 10
                    button.rect.y += 10
                    button.label.rect.y += 10
            elif event.button == 5 and list(self.buttons.values())[len(self.buttons)-1].rect.bottom > config.height:
                for button in self.buttons.values():
                    button.y -= 10
                    button.rect.y -= 10
                    button.label.rect.y -= 10    

    def change_asset(self, asset):
        self.buttons[config.board_asset].update_color(Colors.WHITE)
        config.board_asset = asset
        self.buttons[asset].update_color(Colors.GREEN)

    
