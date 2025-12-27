import pygame
import pygame_gui
import random
import json
import os
from sys import exit
from time import sleep
import settings
from init import init_game

class Obstacle:

    def __init__(self, obs_img, x, y, speed, is_bird=False):

        self.obs_img = obs_img
        self.rect = self.obs_img.get_rect(midbottom=(x, y))
        self.speed = speed
        self.is_bird = is_bird
        self.mask = pygame.mask.from_surface(self.obs_img)
    
    def update_obstacle(self):
        self.rect.x -= self.speed
    
    def draw_obstacle(self , surface):
        surface.blit(self.obs_img , self.rect)
    
    def reposition_obstacle(self, obs_ground_y, screen_height , ratio_h):
        if self.is_bird:
            self.rect.bottom = obs_ground_y - int(screen_height * 0.125)
        else:
            self.rect.bottom = obs_ground_y + int(50 *  ratio_h)


class Game(init_game):

    def __init__(self):

        super().__init__()

        self.key_dictionary = {
            "Options": pygame.K_ESCAPE,
            "Quit" : pygame.K_0,
            self.fixed_screen_size : pygame.K_1,
            "Fullscreen" : pygame.K_2,
            "Turn on Music": pygame.K_3,
            "Turn off Music": pygame.K_4,
            "Volume Down": pygame.K_5,
            "Volume Up": pygame.K_6,
            "Jump": pygame.K_w,
            "Crouch": pygame.K_s
        }
        self.penguin_rect = self.penguin.get_rect(midbottom=(150, self.ground_y))
        self.gravity = 0
        self.is_jumping = False
        self.obstacles = []
        self.obstacle_timer = 0

    
    def show_options_menu(self):

        def create_options_ui() -> tuple:

            self.gui_mgr.clear_and_reset()
            c_x = (self.screen_width - self.button_width) // 2

            spacing_y = self.button_height + int(30 * self.ratio_h)
            start_y = self.screen_height // 2 - spacing_y
        
            cont_btn = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((c_x, start_y), (self.button_width, self.button_height)),
                text="Continue to Play", manager=self.gui_mgr, object_id="@blue_button")
        
            sett_btn = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((c_x, start_y + spacing_y), (self.button_width, self.button_height)),
                text="Settings", manager=self.gui_mgr, object_id="@orange_button")
        
            quit_btn = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((c_x, start_y + spacing_y * 2), (self.button_width, self.button_height)),
                text="Quit", manager=self.gui_mgr, object_id="@red_button")
            
            return cont_btn , sett_btn , quit_btn

        self.current_menu = "options"
        cont_btn , sett_btn , quit_btn = create_options_ui()
        pause_start_time = pygame.time.get_ticks()

        waiting = True
        while waiting:

            self.dt = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == self.key_dictionary[self.fixed_screen_size]:
                            self.handle_resize(False)
                            cont_btn, sett_btn, quit_btn = create_options_ui()
                    elif event.key == self.key_dictionary["Fullscreen"]:
                        self.handle_resize(True)
                        cont_btn, sett_btn, quit_btn = create_options_ui()
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == cont_btn:
                        pause_duration = pygame.time.get_ticks() - pause_start_time
                        self.start_ticks += pause_duration
                        self.countdown(); waiting = False
                    elif event.ui_element == sett_btn:
                        settings.Settings(self).display_settings()
                        cont_btn , sett_btn , quit_btn = create_options_ui()
                    elif event.ui_element == quit_btn:
                        pygame.quit(); exit()
                        
                self.gui_mgr.process_events(event)
            
            self.gui_mgr.update(self.dt)

            self.set_blits(self.background , self.background_x1 , self.background_x2 , 0 , 0)
            self.set_blits(self.ground , self.ground_x1 , self.ground_x2 , self.screen_height - self.ground.get_height() , self.screen_height - self.ground.get_height())
            self.display_surface.blit(self.penguin, self.penguin_rect)

            for obs in self.obstacles:
                obs.draw_obstacle(self.display_surface)

            self.gui_mgr.draw_ui(self.display_surface)
            pygame.display.flip()
        
        self.set_buttons()


    def countdown(self):

        countdown_start_time = pygame.time.get_ticks()

        for i in range(3, 0, -1):
            self.set_blits(self.background , self.background_x1 , self.background_x2 , 0 , 0)
            self.set_blits(self.ground , self.ground_x1 , self.ground_x2 , self.screen_height - self.ground.get_height() , self.screen_height - self.ground.get_height())
            self.display_surface.blit(self.penguin, self.penguin_rect)

            for obs in self.obstacles:
                obs.draw_obstacle(self.display_surface)

            txt = self.countdown_font.render(str(i), True, (200, 0, 0))
            rect = txt.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.display_surface.blit(txt, rect)

            pygame.display.flip()
            pygame.time.delay(1000)
        
        countdown_duration = pygame.time.get_ticks() - countdown_start_time
        self.start_ticks += countdown_duration

    
    def show_game_over_screen(self):

        def create_game_over_ui() -> tuple:
            
            self.gui_mgr.clear_and_reset()
            c_x = (self.screen_width - self.button_width) // 2

            spacing_height = int(50 * self.ratio_h)
            start_y = self.screen_height // 2 - int(220 * self.ratio_h)
            
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((c_x, start_y), (self.button_width + 100, spacing_height)),
                text="GAME OVER!", manager=self.gui_mgr, object_id="#gameover_screen_font")
        
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((c_x, start_y + spacing_height), (self.button_width + 100, spacing_height)),
                text=f"your score: {int(self.score)}", manager=self.gui_mgr, object_id="#gameover_screen_font")
                
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((c_x, start_y + spacing_height * 2), (self.button_width + 100, spacing_height)),
                text=f"highest score: {int(self.highest_score)}", manager=self.gui_mgr, object_id="#gameover_screen_font")
            
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((c_x, start_y + spacing_height * 3), (self.button_width + 100, spacing_height)),
                text=f"total time: {int(self.elapsed_time / 60)} min {self.elapsed_time % 60} sec", 
                manager=self.gui_mgr, 
                object_id="#gameover_screen_font")
            
            button_y = self.screen_height // 2
            button_spacing_height = self.button_height + int(20 * self.ratio_h)

            play_again_btn = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((c_x, button_y), (self.button_width, self.button_height)),
                text="Play Again", manager=self.gui_mgr, object_id="@blue_button")
            
            main_menu_btn = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((c_x, button_y + button_spacing_height), (self.button_width, self.button_height)),
                text="Main Menu", manager=self.gui_mgr, object_id="@orange_button")
            
            quit_btn = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((c_x, button_y + button_spacing_height * 2), (self.button_width, self.button_height)),
                text="Quit", manager=self.gui_mgr, object_id="@red_button")
        
            return play_again_btn , main_menu_btn , quit_btn

        self.current_menu = "game"
        current_btns = create_game_over_ui()

        waiting = True
        while waiting:

            self.display_surface.blit(self.background , (0,0))
            self.dt = self.clock.tick(60) / 1000.0
            self.set_key_combinations()

            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == self.key_dictionary[self.fixed_screen_size] or \
                    event.key == self.key_dictionary["Fullscreen"]:
                        is_fullscreen = (event.key == self.key_dictionary["Fullscreen"])
                        self.handle_resize(is_fullscreen) 
                        current_btns = create_game_over_ui()
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == current_btns[0]:
                        self.play = True
                        waiting = False
                        sleep(0.5)
                    elif event.ui_element == current_btns[1]:
                        self.gui_mgr.clear_and_reset()
                        self.set_buttons()
                        self.play = False 
                        waiting = False
                    elif event.ui_element == current_btns[2]:
                        pygame.quit(); exit()
                        
                self.gui_mgr.process_events(event)
            
            self.gui_mgr.update(self.dt)
            self.gui_mgr.draw_ui(self.display_surface)
            pygame.display.flip()

    
    def set_key_combinations2(self):

        self.set_key_combinations()
        keys = pygame.key.get_pressed()
        if keys[self.key_dictionary[self.fixed_screen_size]]:
                self.is_fullscreen = False
                self.handle_resize(False)
        elif keys[self.key_dictionary["Fullscreen"]]:
            if not (self.display_surface.get_flags() & pygame.FULLSCREEN):
                self.is_fullscreen = False
                self.handle_resize(True)
        if keys[self.key_dictionary["Options"]]:
            self.show_options_menu()
        if keys[self.key_dictionary["Jump"]] and not self.is_jumping:
            self.gravity = -36 * self.ratio_h
            self.is_jumping = True
        if keys[self.key_dictionary["Crouch"]] and not self.is_jumping:
            self.current_penguin_img = self.penguin_crouch
            self.penguin_rect = self.current_penguin_img.get_rect(midbottom=(self.penguin_rect.centerx , self.ground_y + int(50 * self.ratio_h)))
        else:
            self.current_penguin_img = self.penguin
            
            if not self.is_jumping:
                self.penguin_rect = self.current_penguin_img.get_rect(midbottom=(self.penguin_rect.centerx , self.ground_y))
            else:
                self.penguin_rect = self.current_penguin_img.get_rect(center= self.penguin_rect.center)



    def save_keys(self):
        with open(os.path.join('JSON' , 'key_settings.json'), "w") as f:
            json.dump(self.key_dictionary, f)


    def load_keys(self):
        try:
            with open(os.path.join('JSON' , 'key_settings.json'), "r") as f:
                loaded_keys = json.load(f)
                self.key_dictionary = {action: int(key) for action, key in loaded_keys.items()}
        except FileNotFoundError:
            pass


    def set_positions(self):

        self.score += 0.1

        if self.score > self.highest_score:
            self.highest_score = self.score
            with open(os.path.join('codes' , 'highest_score.txt'), "w" , encoding="utf-8") as file:
                file.write(str(int(self.highest_score)))

        if self.background_x1 - 5 <= self.screen_width * -1:
            self.background_x1 = self.screen_width
        else:
            self.background_x1 -= 5
        if self.background_x2 - 5 <= self.screen_width * -1:
            self.background_x2 = self.screen_width
        else:
            self.background_x2 -= 5
        
        self.gravity += 1.1 * self.ratio_h
        self.penguin_rect.y += self.gravity
        if self.penguin_rect.bottom >= self.ground_y:
            self.penguin_rect.bottom = self.ground_y
            self.is_jumping = False
            self.gravity = 0
        elif not self.is_jumping:
            self.penguin_rect.bottom = self.ground_y
        
        difficulty_multiplier = 1.0 + (self.elapsed_time / 150.0)
        current_speed = (self.obstacle_base_speed * self.ratio_w) + int(self.score / 150) * difficulty_multiplier
        self.ground_x1 -= current_speed
        self.ground_x2 -= current_speed

        if self.ground_x1 <= -self.screen_width:
            self.ground_x1 = self.ground_x2 + self.screen_width
        if self.ground_x2 <= -self.screen_width:
            self.ground_x2 = self.ground_x1 + self.screen_width

        current_min = max(30, int(100 / difficulty_multiplier))
        current_max = max(60, int(200 / difficulty_multiplier))

        if self.elapsed_time > 0 and self.elapsed_time % 18 == 0:
            if self.elapsed_time != self.last_speed_up_milestone:
                self.show_speed_up_text = True
                self.speed_up_timer = pygame.time.get_ticks() 
                self.last_speed_up_milestone = self.elapsed_time

        self.obstacle_timer += 1
        can_spawn = True
        if self.obstacles:
            last_obstacle = self.obstacles[-1]
            min_distance = 320 * self.ratio_w

            if not last_obstacle.is_bird:
                min_distance = 470 * self.ratio_w

            if last_obstacle.rect.x > self.screen_width - min_distance:
                can_spawn = False


        if self.obstacle_timer > random.randint(current_min , current_max) and can_spawn:
            if random.random() < 0.7:
                new_obstacle = Obstacle(self.bear, self.screen_width, self.ground_y + int(50 * self.ratio_h), current_speed, is_bird=False)
            else:
                new_obstacle_y = self.ground_y - int(self.screen_height * 0.13)
                new_obstacle = Obstacle(self.bird, self.screen_width, new_obstacle_y, current_speed + 2, is_bird=True)

            self.obstacles.append(new_obstacle)
            self.obstacle_timer = 0
        
        for obs in self.obstacles[:]:
            obs.update_obstacle()
            if obs.rect.right < 0:
                self.obstacles.remove(obs)
            
            penguin_mask = pygame.mask.from_surface(self.current_penguin_img)
            offset = obs.rect.x - self.penguin_rect.x , obs.rect.y - self.penguin_rect.y

            if penguin_mask.overlap(obs.mask , offset):
                self.play = False

      
    def run(self):
        while True:
            self.set_main_screen()
            self.score = 0
            self.start_ticks = pygame.time.get_ticks()
            self.obstacles = []
            
            self.penguin_rect = self.penguin.get_rect(midbottom=(150, self.ground_y - 100))
            self.is_jumping = False
            self.gravity = 0

            while self.play:
                self.clock.tick(60)
                self.elapsed_time = (pygame.time.get_ticks() - self.start_ticks) // 1000

                self.set_blits(self.background , self.background_x1 , self.background_x2 , 0 , 0)
                self.set_blits(self.ground , self.ground_x1 , self.ground_x2 , self.screen_height - self.ground.get_height() , self.screen_height - self.ground.get_height())
                self.set_positions()
                
                self.set_key_combinations2()

                score_surface = self.font.render(f"score: {int(self.score)}" , antialias=True, color=(255,255,255))
                self.display_surface.blit(score_surface, (20 , 20))

                highest_score_surface = self.font.render(f"highest score: {int(self.highest_score)}" , antialias=True , color =(255,255,255))
                self.display_surface.blit(highest_score_surface , (320 , 20))

                if self.show_speed_up_text:
                    current_time = pygame.time.get_ticks()
                    if current_time - self.speed_up_timer < 2000:
                        if (current_time // 250) % 2 == 0:
                            speed_text = self.countdown_font.render("SPEED UP!", True, (255, 255, 255))
                            text_rect = speed_text.get_rect(center=(self.screen_width // 2, self.screen_height // 3))
                            self.display_surface.blit(speed_text, text_rect)
                    else:
                        self.show_speed_up_text = False

                time_surface = self.font.render(f"time: {int(self.elapsed_time / 60)} min {self.elapsed_time % 60} sec" , True , (255,255,255))
                time_rect = time_surface.get_rect(topright=(self.screen_width - 20, 20))
                self.display_surface.blit(time_surface, time_rect)

                self.display_surface.blit(self.current_penguin_img , self.penguin_rect)
                for obs in self.obstacles:
                    obs.draw_obstacle(self.display_surface)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                
                pygame.display.flip()
            
            self.show_game_over_screen()


if __name__ == '__main__':
    Game().run()