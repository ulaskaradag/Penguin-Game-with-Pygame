import pygame
import pygame_gui
import os
import settings
from time import sleep


class init_game:

    def __init__(self):

        pygame.init()
        pygame.mixer.init()

        pygame.display.set_caption('Penguin Game')
        self.fixed_screen_width = pygame.display.Info().current_w - 50
        self.fixed_screen_height = pygame.display.Info().current_h - 80
        self.fixed_screen_size = str(self.fixed_screen_width) + "x" + str(self.fixed_screen_height) + " Screen"
        self.display_surface = pygame.display.set_mode((0,0) , pygame.FULLSCREEN)
        self.fullscreen_width = pygame.display.Info().current_w
        self.fullscreen_height = pygame.display.Info().current_h
        self.is_fullscreen = True
        self.update_dimensions()

        self.open_screen = True
        self.play = False
        self.score = 0

        with open(os.path.join('codes' , 'highest_score.txt') , "r" , encoding="utf-8") as file:
            self.highest_score = int(file.readline().strip())
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(os.path.join('font' , 'penguin_game.ttf') , 40)
        self.countdown_font = pygame.font.Font(os.path.join('font' , 'penguin_game.ttf'), 100)

        self.set_image_assets()
        self.set_sound()

        self.gui_mgr = pygame_gui.UIManager((self.display_surface.get_width(), self.display_surface.get_height()), 
                                             os.path.join('JSON' , 'theme.json'))
        self.gui_mgr.add_font_paths("game_font", os.path.join('font' , 'penguin_game.ttf'))
        self.gui_mgr.preload_fonts([{'name': 'game_font', 'point_size': 18, 'style': 'regular'},
                            {'name': 'game_font', 'point_size': 20, 'style': 'regular'},
                            {'name': 'game_font', 'point_size': 24, 'style': 'regular'},
                            {'name': 'game_font', 'point_size': 32, 'style': 'regular'},
                            {'name': 'game_font', 'point_size': 40, 'style': 'regular'}])
        self.gui_mgr.get_theme().load_theme(os.path.join('JSON', 'theme.json'))

        self.current_menu = "main"
        self.set_buttons()

        self.min_spawn_time = 100
        self.max_spawn_time = 200
        self.obstacle_base_speed = 10

        self.start_ticks = 0
        self.elapsed_time = 0

        self.show_speed_up_text = False
        self.speed_up_timer = 0
        self.last_speed_up_milestone = 0

    
    #Dynamically recalculate the size of the screen and the scaling ratios to ensure the rendering works on two different resolutions that game supports
    def update_dimensions(self):

        self.screen_width = self.display_surface.get_width()
        self.screen_height = self.display_surface.get_height()

        self.ratio_w = self.screen_width / self.fixed_screen_width
        self.ratio_h = self.screen_height / self.fixed_screen_height

        if hasattr(self, 'gui_mgr'):
            self.gui_mgr.set_window_resolution((self.screen_width, self.screen_height))


    #Keeping the right positioning of objects and the layout of the UI in case of screen size change
    def handle_resize(self,is_fullscreen = False):

        if is_fullscreen:
            self.display_surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.screen_width = self.display_surface.get_width()
            self.screen_height = self.display_surface.get_height()
        else:
            self.display_surface = pygame.display.set_mode((self.fixed_screen_width , self.fixed_screen_height)) 
            size = pygame.display.get_window_size()
            self.screen_width , self.screen_height = size[0] , size[1]
            self.display_surface = pygame.display.set_mode((self.screen_width , self.screen_height))

        self.update_dimensions()
        self.set_image_assets() 

        if hasattr(self, 'penguin_rect'):
            self.penguin_rect = self.current_penguin_img.get_rect(midbottom=(150, self.ground_y))
    
        if hasattr(self, 'obstacles'):
            for obs in self.obstacles:
                obs.reposition_obstacle(self.ground_y, self.screen_height , self.ratio_h)

        self.gui_mgr.set_window_resolution((self.screen_width, self.screen_height))
        self.gui_mgr.get_theme().load_theme(os.path.join('JSON', 'theme.json'))
        
        if self.current_menu == "main":
            self.set_buttons()

    
    #Initializes the background music
    def set_sound(self):
            
            pygame.mixer.music.load(os.path.join('music' , 'theme_music.wav'))
            pygame.mixer.music.set_volume(0.5) # 50%
            pygame.mixer.music.play(-1) #Infinite loop


    #Loads and scales all image assets dynamically
    def set_image_assets(self):

        self.background = pygame.image.load(os.path.join('images', 'mountain.png')).convert()
        self.background = pygame.transform.scale(self.background , (self.screen_width , self.screen_height))

        self.logo = pygame.image.load(os.path.join('images' , 'logo.png')).convert_alpha()
        self.logo = pygame.transform.scale(self.logo , (self.screen_width * 0.25 , self.screen_height * 0.5))

        self.ground = pygame.image.load(os.path.join('images' , 'ground.png')).convert_alpha()
        self.ground = pygame.transform.scale(self.ground , (self.screen_width , self.screen_height * 0.3))
        self.ground_y = self.screen_height - int(self.screen_height * 0.11) + int(20 * self.ratio_h)


        self.penguin = pygame.image.load(os.path.join('images' , 'penguin.png')).convert_alpha()
        self.penguin = pygame.transform.scale(self.penguin , (self.screen_width * 0.13 , self.screen_width * 0.13))
        self.penguin_rect = self.penguin.get_rect(midbottom=(150 , self.ground_y))

        self.penguin_crouch = pygame.image.load(os.path.join('images' , 'penguin_crouch.png'))
        self.penguin_crouch = pygame.transform.scale(self.penguin_crouch , (self.screen_width * 0.2 , self.screen_width * 0.2))

        self.current_penguin_img = self.penguin

        self.bear = pygame.image.load(os.path.join('images' , 'bear.png')).convert_alpha()
        self.bear = pygame.transform.scale(self.bear , (self.screen_width * 0.2 , self.screen_width * 0.2))

        self.bird = pygame.image.load(os.path.join('images' , 'bird.png')).convert_alpha()
        self.bird = pygame.transform.scale(self.bird , (self.screen_width * 0.2 , self.screen_width * 0.2))

        self.background_x1 = 0
        self.background_x2 = self.screen_width

        self.ground_x1 = 0
        self.ground_x2 = self.screen_width

    
    #Draws the same graphical surface twice at different horizontal positions on the screen to apply infinite scrolling effect
    def set_blits(self, surface ,pos_x1: int , pos_x2: int , pos_y1: int , pos_y2: int):  

        self.display_surface.blit(surface , (pos_x1 , pos_y1))
        self.display_surface.blit(surface , (pos_x2 , pos_y2))


    #Sets main screen menu buttons
    def set_buttons(self):

        self.gui_mgr.clear_and_reset()
        
        self.button_width = int(self.screen_width * 0.15)
        self.button_height = int(self.screen_height * 0.06)
        self.center_pos_x = (self.screen_width - self.button_width) // 2

        self.play_button_pos_y = self.screen_height // 2
        self.play_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.center_pos_x , self.play_button_pos_y), 
                                      (self.button_width , self.button_height)),
            text="Play",
            manager=self.gui_mgr,
            object_id="@blue_button"
        )

        self.logo_pos_x = (self.screen_width - self.logo.get_width()) // 2
        self.logo_pos_y = self.play_button_pos_y - self.logo.get_height() + 40
        self.logo_rect = self.logo.get_rect(topleft=(self.logo_pos_x , self.logo_pos_y))

        self.settings_button_pos_y = self.play_button_pos_y + self.button_height + 25
        self.settings_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.center_pos_x , self.settings_button_pos_y), 
                                      (self.button_width , self.button_height)),
            text="Settings",
            manager=self.gui_mgr,
            object_id="@orange_button"
        )

        self.quit_button_pos_y = self.settings_button_pos_y + self.button_height + 25
        self.quit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.center_pos_x , self.quit_button_pos_y), 
                                      (self.button_width , self.button_height)),
            text="Quit",
            manager = self.gui_mgr,
            object_id="@red_button"
        )

    
    #Runs the main menu loop and handles user interactions
    def set_main_screen(self):

        self.current_menu = "main"
        
        while self.open_screen and not self.play:
            
            self.dt = self.clock.tick(60) / 1000.0

            if hasattr(self, 'set_key_combinations'):
                self.set_key_combinations()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); exit()
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.play_button:
                        self.play = True; sleep(0.5)
                    elif event.ui_element == self.settings_button:
                        settings.Settings(self).display_settings(); self.set_buttons()
                    elif event.ui_element == self.quit_button:
                        pygame.quit(); exit()
                
                self.gui_mgr.process_events(event)
            
            self.gui_mgr.update(self.dt)
            self.set_blits(self.background , self.background_x1 , self.background_x2 , 0 , 0)
            self.display_surface.blit(self.logo , self.logo_rect)
            self.gui_mgr.draw_ui(self.display_surface)
            pygame.display.flip()


    #Take cares of keyboard shortcuts
    def set_key_combinations(self):
        
        keys = pygame.key.get_pressed()

        if keys[self.key_dictionary["Quit"]]:
            pygame.quit(); exit()
        elif keys[self.key_dictionary[self.fixed_screen_size]]:
                self.handle_resize(False); pygame.event.clear()
        elif keys[self.key_dictionary["Fullscreen"]]:
            if not (self.display_surface.get_flags() & pygame.FULLSCREEN):
                self.handle_resize(True)
        elif keys[self.key_dictionary["Turn on Music"]]:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play(-1) #play music with infinite loop
            else:
                pygame.mixer.music.unpause()
        elif keys[self.key_dictionary["Turn off Music"]]:
            pygame.mixer.music.pause()
        elif keys[self.key_dictionary["Volume Down"]]:
            current_vol = pygame.mixer.music.get_volume()
            pygame.mixer.music.set_volume(max(0.0 , current_vol - 0.01))
        elif keys[self.key_dictionary["Volume Up"]]:
            current_vol = pygame.mixer.music.get_volume()
            pygame.mixer.music.set_volume(min(current_vol + 0.01 , 1.0))
