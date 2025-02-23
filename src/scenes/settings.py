import pygame
from scenes.scene import Scene
from config import config
from gui import Label, RectButton, create_rect_surface
from constants import Colors, Fonts, available_board, available_piece, available_sound
from utils import generate_piece_images, generate_board_image, load_image, generate_sounds, resize_image

#TODO Faire les sons mais flemme

class SettingsMenu(Scene):
    def __init__(self):
        super().__init__()
        self.volume_bar = VolumeBar()
        self.piece_assets_menu = PieceAssetsMenu(self)
        self.board_assets_menu = BoardAssetsMenu(self)
        self.sound_assets_menu = SoundAssetsMenu(self)
        self.assets_menu = None
        self.filter = create_rect_surface(Colors.BLACK, config.width, config.height, 0, 150)
        self.garry = load_image('assets/images/gary.png', (config.width*0.6, config.height))

    def create_buttons(self):
        self.buttons = {
            "piece": RectButton(config.width*0.2, config.height*0.2, config.width*0.3, config.height*0.1, 0, Colors.WHITE, 'piece assets', Fonts.GEIZER, Colors.BLACK, lambda:self.change_assets_menu(self.piece_assets_menu)),
            "board": RectButton(config.width*0.2, config.height*0.35, config.width*0.3, config.height*0.1, 0, Colors.WHITE, 'board assets', Fonts.GEIZER, Colors.BLACK, lambda:self.change_assets_menu(self.board_assets_menu)),
            "sound": RectButton(config.width*0.2, config.height*0.5, config.width*0.3, config.height*0.1, 0, Colors.WHITE, 'sound assets', Fonts.GEIZER, Colors.BLACK, lambda:self.change_assets_menu(self.sound_assets_menu))
        }

    def change_assets_menu(self, menu):
        self.assets_menu = menu
    
    def render(self, screen):
        screen.fill(Colors.BLACK.value)
        super().render(screen)
        screen.blit(self.garry, (config.width*0.4, 0))
        self.volume_bar.draw(screen)
        if self.assets_menu:
            screen.blit(self.filter)
            self.assets_menu.render(screen)

    def update(self):
        if not self.assets_menu:
            super().update()
            self.volume_bar.update()
        else:
            self.assets_menu.update()

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        if not self.assets_menu:
            super().handle_event(event)
        else:
            self.assets_menu.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:           
                if mouse_pos[0] < list(self.assets_menu.buttons.values())[0].rect.left or mouse_pos[0] > list(self.assets_menu.buttons.values())[0].rect.right:
                    self.change_assets_menu(None)

    
class PieceAssetsMenu(Scene):
    def __init__(self, settings_menu):
        super().__init__()
        self.settings_menu = settings_menu
        self.piece_images = generate_piece_images()
        self.buttons[config.piece_asset].update_color(Colors.GREEN)
        self.board_image = generate_board_image()
        self.board_clip_rect = pygame.Rect(0, 0, config.tile_size*6, config.tile_size*2)

    def create_buttons(self):
        self.buttons = {asset: RectButton(config.width*0.25, config.height*0.05+(config.height*0.1*i), config.width*0.3, config.height*0.1, 0, Colors.WHITE, asset, Fonts.GEIZER, Colors.BLACK, lambda:None) for i, asset in enumerate(available_piece)}

    def create_labels(self):
        self.labels = {'selected_asset': Label((int(config.width*0.72), int(config.height*0.65)), config.piece_asset, Fonts.GEIZER, int(config.height*0.1), Colors.BLACK, create_rect_surface(Colors.WHITE, int(config.width*0.3), int(config.height*0.1), int(config.height*0.075)), (int(config.width*0.72), int(config.height*0.65)))}

    def render(self, screen):
        super().render(screen)
        screen.blit(self.board_image, dest=(config.width*0.515, config.height*0.3), area=self.board_clip_rect)
        if config.piece_asset == 'blindfold':
            return
        elif config.piece_asset == 'mono':
            for i, image in enumerate(self.piece_images.values()):
                screen.blit(image, (config.width*0.515+(config.tile_size*i), config.height*0.3+config.tile_size//2))
        else:
            for i, piece in enumerate(self.piece_images.items()):
                notation, image = piece[0], piece[1]
                i = i%6
                if notation[0] == 'w':
                    screen.blit(image, (config.width*0.515+(config.tile_size*i), config.height*0.3))
                else:
                    screen.blit(image, (config.width*0.515+(config.tile_size*i), config.height*0.3+config.tile_size))


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
        if asset != 'blindfold':
            self.piece_images = generate_piece_images()
        self.labels['selected_asset'].update_text(config.piece_asset)


class BoardAssetsMenu(Scene):
    def __init__(self, settings_menu):
        super().__init__()
        self.settings_menu = settings_menu
        self.board_image = resize_image(generate_board_image(), (config.height*0.75, config.height*0.75))
        self.buttons[config.board_asset].update_color(Colors.GREEN) 

    def create_buttons(self):
        self.buttons = {asset: RectButton(config.width*0.2, config.height*0.05+(config.height*0.1*i), config.width*0.3, config.height*0.1, 0, Colors.WHITE, asset, Fonts.GEIZER, Colors.BLACK, lambda:None) for i, asset in enumerate(available_board)}

    def create_labels(self):
        self.labels = {'selected_asset': Label((int(config.width*0.69), int(config.height*0.9)), config.board_asset, Fonts.GEIZER, int(config.height*0.1), Colors.BLACK, create_rect_surface(Colors.WHITE, int(config.width*0.32), int(config.height*0.1), int(config.height*0.075)), (int(config.width*0.69), int(config.height*0.9)))}

    def render(self, screen):
        super().render(screen)
        screen.blit(self.board_image, (config.width*0.47, config.margin))

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
        self.board_image = resize_image(generate_board_image(), (config.height*0.75, config.height*0.75))
        self.settings_menu.piece_assets_menu.board_image = generate_board_image()
        self.labels['selected_asset'].update_text(config.board_asset)


class SoundAssetsMenu(Scene):
    def __init__(self, settings_menu):
        super().__init__()
        self.settings_menu = settings_menu
        self.sounds = generate_sounds()
        self.buttons[config.sound_asset].update_color(Colors.GREEN)

    def create_buttons(self):
        self.buttons = {asset: RectButton(config.width*0.2, config.height*0.1+(config.height*0.1*i), config.width*0.3, config.height*0.1, 0, Colors.WHITE, asset, Fonts.GEIZER, Colors.BLACK, lambda:None) for i, asset in enumerate(available_sound)}

    def render(self, screen):
        super().render(screen)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for asset, button in self.buttons.items():
                    if button.is_clicked():
                        self.change_asset(asset)

    def change_asset(self, asset):
        self.buttons[config.sound_asset].update_color(Colors.WHITE)
        config.sound_asset = asset
        self.buttons[asset].update_color(Colors.GREEN)
        self.sounds = generate_sounds()


class VolumeBar:
    def __init__(self):
        self.rect = pygame.Rect(0, config.height * 0.7, config.width * 0.3, config.height * 0.07)
        self.rect.centerx = config.width*0.2
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