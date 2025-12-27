import pygame
import pygame_gui
from sys import exit
from main import Game

class Settings:

    def __init__(self , game_obj):

        self.game = game_obj
        self.waiting_for_key = False
        self.open_settings = False
        self.key_to_change = None
        self.key_labels = {}
    

    def create_settings_ui(self):

        self.game.gui_mgr.clear_and_reset()
    
        self.row_height = int(self.game.screen_width * 0.05)
        self.label_width = int(self.game.screen_width * 0.25)       
        self.key_val_width = int(self.game.screen_width * 0.15)     
        self.button_width = int(self.game.screen_width * 0.15)      
        self.center_x = self.game.screen_width // 2

        self.change_buttons = {}

        self.back_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((20, 20), (50, 50)),
            text="<-",
            manager=self.game.gui_mgr,
            object_id="@blue_button"
        )

        self.scroll_container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect((0, 0), (self.game.screen_width, self.game.screen_height)),
            manager=self.game.gui_mgr,
        )
        
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.center_x - (self.game.screen_width // 4), 30),
                                      (self.game.screen_width // 2, self.row_height)),
            text="Key Settings",
            manager=self.game.gui_mgr,
            container=self.scroll_container,
            object_id="#settings_title"
        )
        
        y_offset = 120
        for action, key in self.game.key_dictionary.items():
            
            action_rect = pygame.Rect(0, 0, self.label_width, self.row_height)
            action_rect.topright = (self.center_x - 100, y_offset)
            pygame_gui.elements.UILabel(
                relative_rect=action_rect, text=f"{action}:",
                manager=self.game.gui_mgr,
                container=self.scroll_container,
                object_id="#action_label"
            )

            key_rect = pygame.Rect(0, 0, self.key_val_width, self.row_height)
            key_rect.centerx = self.center_x
            key_rect.top = y_offset
            key_label = pygame_gui.elements.UILabel(
                relative_rect=key_rect, 
                text=pygame.key.name(key).upper(),
                manager=self.game.gui_mgr,
                container=self.scroll_container, 
                object_id="#key_display"
            )
            self.key_labels[action] = key_label

            change_btn_rect = pygame.Rect(0, 0, self.button_width, self.row_height)
            change_btn_rect.topleft = (self.center_x + 150, y_offset)
            change_btn = pygame_gui.elements.UIButton(
                relative_rect=change_btn_rect,
                text="Change",
                manager=self.game.gui_mgr,
                container=self.scroll_container,
                object_id="@blue_button"
            )
            self.change_buttons[change_btn] = action

            y_offset += self.row_height + 15

        self.scroll_container.set_scrollable_area_dimensions((self.game.screen_width , y_offset + 50))


    def display_settings(self):

        self.game.current_menu = "settings"

        self.open_settings = True
        self.create_settings_ui()

        while self.open_settings:

            self.dt = self.game.clock.tick(60) / 1000.0

            if not self.waiting_for_key:
                self.game.set_key_combinations()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == self.game.key_dictionary[self.game.fixed_screen_size] or \
                    event.key == self.game.key_dictionary["Fullscreen"]:
                        is_fullscreen = (event.key == self.game.key_dictionary["Fullscreen"])
                        self.game.handle_resize(is_fullscreen)
                        self.create_settings_ui()
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if self.waiting_for_key and event.type == pygame.KEYUP:
                    new_key = event.key
                    action_to_change = self.key_to_change

                    duplicate_action = None
                    for action , key in self.game.key_dictionary.items():
                        if key == new_key and action != action_to_change:
                            duplicate_action = action
                            break

                    if duplicate_action:

                        old_key = self.game.key_dictionary[action_to_change]
                        self.game.key_dictionary[duplicate_action] = old_key
                        self.key_labels[duplicate_action].set_text(pygame.key.name(old_key).upper())

                    self.game.key_dictionary[action_to_change] = new_key
                    key_display_name = pygame.key.name(new_key).upper()
                    self.key_labels[action_to_change].set_text(key_display_name)
                
                    self.game.save_keys()

                    self.waiting_for_key = False
                    self.key_to_change = None
                    pygame.event.clear()
                    continue

                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.back_btn:
                        self.open_settings = False
                    elif event.ui_element in self.change_buttons:
                        self.key_to_change = self.change_buttons[event.ui_element]
                        self.waiting_for_key = True
                        self.key_labels[self.key_to_change].set_text("PRESS ANY KEY")
   
                self.game.gui_mgr.process_events(event)
        
            self.game.gui_mgr.update(self.dt)
            self.game.set_blits(self.game.background , 0 , 0 , 0 , 0)
            self.game.gui_mgr.draw_ui(self.game.display_surface)

            pygame.display.flip()
        self.game.gui_mgr.clear_and_reset()
