import re
from queue import *

import pygame

from network import *
from player import Player
from timer import Timer
from words_client import Word
from png_sprite import *


class Game:

    def __init__(self):

        # game user
        pygame.init()
        self.net = Network()
        self.player_me = Player('Katsu', self.net.id)
        self.player_friend = Player('Mon', self.net.id)
        self.player_dict = {self.player_me.id: self.player_me}

        # game interface
        self.width = 1024
        self.height = 720
        self.font = pygame.font.Font('Assets/font/pixelmix.ttf', 32)
        self.player_bongo_me = bongo_sprite
        self.player_bongo_friend = bongo_sprite
        self.player_x_me = 50
        self.player_y_me = 420
        self.player_x_friend = 670
        self.player_y_friend = 420
        # display client -> server
        self.draw_state_me = 0
        self.draw_state_friend = 0

        # display client
        self.draw_index = 0
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('client1')

        # game system
        self.submit_queue = Queue()
        self.status = 0
        self.current_frame_string = ''
        self.word_mem = {}
        self.clock = pygame.time.Clock()
        self.game_state = 0

    def run_lobby(self):
        while self.game_state == 0:
            framerate = self.clock.tick(30)
            data = self.send_data('').split(',')
            self.game_state = int(data[0])
            self.screen.fill(pygame.Color('white'))
            self.screen.blit(pygame.transform.scale(bg_sprite[2], (self.width, self.height)), (0, 0))
            self.draw_connected_player_count(data[1])
            self.draw_text('Player 1: Ready!', 120, 240, 40, 255, 255, 255)
            self.screen.blit(pygame.transform.rotate(pygame.transform.scale(bongo_sprite[1], (1024, 1024)), 12.5),
                             (-40, 40))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            pygame.display.update()

        self.count_down()

    def count_down(self):
        while self.game_state == 1:
            data = self.send_data('').split(',')
            print(data)
            self.game_state = int(data[0])
            self.screen.fill(pygame.Color('white'))
            self.screen.blit(pygame.transform.scale(bg_sprite[2], (self.width, self.height)), (0, 0))
            self.screen.blit(pygame.transform.rotate(pygame.transform.scale(bongo_sprite[1], (1024, 1024)), 12.5),
                             (-40, 40))
            self.draw_countdown_timer(data[1])
            if data[1] == '2':
                self.screen.blit(pygame.transform.rotate(pygame.transform.scale(bongo_sprite[1], (1024, 1024)), 12.5),
                                 (-40, 40))  # mid bottom
                self.screen.blit(pygame.transform.rotate(pygame.transform.scale(bongo_sprite[1], (1024, 1024)), 192.5),
                                 (-110, -550))  # mid top
                self.screen.blit(pygame.transform.rotate(pygame.transform.scale(bongo_sprite[1], (1024, 1024)), 105),
                                 (350, -300))  # right
                self.screen.blit(pygame.transform.rotate(pygame.transform.scale(bongo_sprite[1], (1024, 1024)), -80),
                                 (-550, -180))  # left
            if data[1] == '1':
                self.screen.blit(pygame.transform.rotate(pygame.transform.scale(bongo_sprite[1], (1024, 1024)), 12.5),
                                 (-40, 40))  # mid bottom
                self.screen.blit(pygame.transform.rotate(pygame.transform.scale(bongo_sprite[1], (1024, 1024)), 192.5),
                                 (-110, -550))  # mid top
                self.screen.blit(pygame.transform.rotate(pygame.transform.scale(bongo_sprite[1], (1024, 1024)), 105),
                                 (350, -300))  # right
                self.screen.blit(pygame.transform.rotate(pygame.transform.scale(bongo_sprite[1], (1024, 1024)), -80),
                                 (-550, -180))  # left
                self.screen.blit(pygame.transform.rotate(pygame.transform.scale(bongo_sprite[1], (1024, 1024)), -4),
                                 (-390, 125))  # bottom left
                self.screen.blit(pygame.transform.rotate(pygame.transform.scale(bongo_sprite[1], (1024, 1024)), 35.5),
                                 (240, -70))  # bottom right
                self.screen.blit(pygame.transform.rotate(pygame.transform.scale(bongo_sprite[1], (1024, 1024)), 176),
                                 (350, -500))  # top right
                self.screen.blit(pygame.transform.rotate(pygame.transform.scale(bongo_sprite[1], (1024, 1024)), 205.5),
                                 (-620, -610))  # top left
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            pygame.display.update()

        self.start_game()

    def start_game(self):

        running = True
        backspace_clock = Timer()

        while running:
            framerate = self.clock.tick(30)
            backspace_clock.tick()
            keys = pygame.key.get_pressed()

            player_dict, word_dict = self.parse_data(self.current_frame_string)
            self.sync_data(player_dict, word_dict)

            # redraw per frame
            self.draw_state_me = 0
            self.screen.fill(pygame.Color('white'))
            self.screen.blit(pygame.transform.scale(bg_sprite[0], (self.width, self.height)), (0, 0))
            self.screen.blit(pygame.transform.rotate(pygame.transform.scale(bg_sprite[1], (200, 100)), 2), (70, 570))
            self.screen.blit(
                pygame.transform.flip(pygame.transform.rotate(pygame.transform.scale(bg_sprite[1], (200, 100)), 2),
                                      True, False), (750, 570))

            if keys[pygame.K_BACKSPACE] and len(self.player_me.keystrokes) > 0 and backspace_clock.time >= 2:
                backspace_clock.reset()
                self.player_me.keystrokes = self.player_me.keystrokes[:-1]
            for event in pygame.event.get():
                self.bongo_animation(self.player_bongo_me, event)
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.KEYDOWN:
                    if event.unicode.isalpha() or event.unicode == '-':
                        self.player_me.keystrokes += event.unicode
                    elif event.unicode == '\r' or event.key == pygame.K_RETURN:
                        self.player_me.confirm_key = True

            if self.draw_state_me == 0:
                self.draw_bongo_cat(self.player_bongo_me[self.draw_state_friend], 0)

            self.draw_bongo_cat(self.player_bongo_friend[self.draw_state_friend], 1)
            self.screen.blit(pygame.transform.rotate(pygame.transform.scale(addi_sprite[0], (100, 75)), -1), (180, 485))
            self.screen.blit(pygame.transform.rotate(pygame.transform.scale(addi_sprite[1], (110, 80)), 23), (744, 470))
            self.draw_name_me(self.player_me.name)
            self.draw_score_me(self.player_me.score)
            self.draw_name_friend(self.player_friend.name)
            self.draw_score_friend(self.player_friend.score)
            self.draw_current_stroke(self.player_me.keystrokes)

            for word_id in self.word_mem:
                if self.player_me.keystrokes == '':
                    s = False
                else:
                    s = re.search("^" + self.player_me.keystrokes, self.word_mem[word_id].word)
                if s:
                    self.word_mem[word_id].match_text(s.span())
                    self.word_mem[word_id].start_match = True
                    self.print_move_word(self.word_mem[word_id])
                    self.print_move_matching_word(self.word_mem[word_id])
                elif self.word_mem[word_id].start_match:
                    self.word_mem[word_id].start_match = False
                    self.word_mem[word_id].unmatch_text()
                    self.print_move_word(self.word_mem[word_id])
                else:
                    print('print word')
                    self.print_move_word(self.word_mem[word_id])

            print(self.current_frame_string)
            if self.player_me.confirm_key:
                self.current_frame_string = self.send_data(self.player_me.keystrokes)
                self.player_me.keystrokes = ''
                self.player_me.confirm_key = False
            else:
                self.current_frame_string = self.send_data('')

            pygame.display.update()

    def send_data(self, key_strokes):
        if key_strokes != '':
            data = str(self.net.id) + "," + str(self.status) + "," + str(key_strokes)
        else:
            data = str(self.net.id) + "," + str(self.status) + "," + str(' ')
        reply = self.net.send(data)
        return reply

    @staticmethod
    def parse_data(data):
        try:
            player_data, word_data = data.split(":")[0], data.split(":")[1]
            player_list = player_data.split("|")
            word_list = word_data.split("|")
            player_dict = {}
            word_dict = {}
            for player_string in player_list:
                player = player_string.split(",")
                player_dict[player[0]] = player[1:]
            for word_string in word_list:
                word_separated_data = word_string.split(",")
                word_dict[word_separated_data[0]] = word_separated_data
            return player_dict, word_dict
        except:
            return {}, {}

    def sync_data(self, player_data_dict, word_data_dict):
        for player_id in player_data_dict:
            if player_id not in self.player_dict:
                self.player_dict[player_id] = Player('player2', player_id)
            else:
                self.player_dict[player_id].score = player_data_dict[player_id][0]
        for word_data in word_data_dict:
            if word_data in self.word_mem:
                self.word_mem[word_data].x_pos = x = int(word_data_dict[word_data][3])
                self.word_mem[word_data].y_pos = y = int(word_data_dict[word_data][4])
                self.word_mem[word_data].text_rect.topleft = (x, y)
            else:
                self.word_mem[word_data] = Word(int(word_data_dict[word_data][0]), int(word_data_dict[word_data][1]),
                                                int(word_data_dict[word_data][2]), int(word_data_dict[word_data][3]),
                                                int(word_data_dict[word_data][4]))

        keys_to_keep = set(word_data_dict.keys()).intersection(set(self.word_mem.keys()))
        self.word_mem = {k: v for k, v in self.word_mem.items() if k in keys_to_keep}

    def draw_bongo_cat(self, png, user):
        if user == 0:  # draw me
            self.screen.blit(pygame.transform.scale(png, (300, 300)), (self.player_x_me, self.player_y_me))
        if user == 1:  # draw friend
            self.screen.blit(pygame.transform.flip(pygame.transform.scale(png, (300, 300)), True, False), (self.player_x_friend, self.player_y_friend))

    def bongo_animation(self, bongo_state, event):  # bongo state which folder (me or friend)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.draw_state_me = 2
                self.draw_bongo_cat(bongo_state[self.draw_state_me], 0)
            else:
                if self.draw_index % 2 == 0:
                    self.draw_state_me = 4
                    self.draw_bongo_cat(bongo_state[self.draw_state_me], 0)
                if self.draw_index % 2 == 1:
                    self.draw_state_me = 6
                    self.draw_bongo_cat(bongo_state[self.draw_state_me], 0)
                self.draw_index += 1

    def draw_text(self, text, xpos, ypos, font_size, r, g, b):
        font = pygame.font.Font('freesansbold.ttf', font_size)
        text_show = font.render(str(text), True, (r, g, b))
        text_show_rect = text_show.get_rect()
        text_show_rect.center = (xpos, ypos)
        self.screen.blit(text_show, text_show_rect)

    def draw_timer(self,time):
        time_text = self.font.render(str(time), True, pygame.Color('black'))
        time_text_rect = time_text.get_rect()
        time_text_rect.topright = (1010, 10)
        self.screen.blit(time_text, time_text_rect)

    def draw_name_me(self, name):
        name_text = self.font.render('MEOW ' + name, True, pygame.Color('black'))
        name_text_rect = name_text.get_rect()
        name_text_rect.topleft = (10, 10)
        self.screen.blit(name_text, name_text_rect)

    def draw_name_friend(self, name):
        name_text = self.font.render('MEOW ' + name, True, pygame.Color('black'))
        name_text_rect = name_text.get_rect()
        name_text_rect.topright = (1014, 10)
        self.screen.blit(name_text, name_text_rect)

    def draw_score_me(self, score):
        score_text = self.font.render('SCORE: ' + str(score), True, pygame.Color('black'))
        score_text_rect = score_text.get_rect()
        score_text_rect.topleft = (10, 50)
        self.screen.blit(score_text, score_text_rect)

    def draw_score_friend(self, score):
        score_text = self.font.render('SCORE: ' + str(score), True, pygame.Color('black'))
        score_text_rect = score_text.get_rect()
        score_text_rect.topright = (1014, 50)
        self.screen.blit(score_text, score_text_rect)

    def draw_current_stroke(self, current_stroke):
        score_text = self.font.render(current_stroke, True, pygame.Color('black'))
        score_text_rect = score_text.get_rect()
        score_text_rect.midbottom = (512, 710)
        self.screen.blit(score_text, score_text_rect)

    def draw_connected_player_count(self, player_count):
        font = pygame.font.Font('freesansbold.ttf', 50)
        text = font.render('Connected Players:' + str(player_count) + '/2', True, pygame.Color('black'))
        text_rect = text.get_rect()
        text_rect.center = (int(self.width / 2), int(self.height / 2))
        self.screen.blit(text, text_rect)

    def draw_countdown_timer(self, time):
        font = pygame.font.Font('Assets/font/pixelmix.ttf', 50)
        text = font.render('Game Starting In:' + time, True, pygame.Color('black'))
        if time == '1':
            text = font.render('Game Starting In:' + time + '!', True, pygame.Color('black'))
        text_rect = text.get_rect()
        text_rect.center = (int(self.width / 2), int(self.height / 2))
        self.screen.blit(text, text_rect)

    def print_move_word(self, w):
        self.screen.blit(w.text, w.text_rect)
        # w.text_rect.move_ip(0, w.fall_speed)

    def print_move_matching_word(self, w):
        self.screen.blit(w.matching_text, w.matching_text_rect)
        # w.matching_text_rect.move_ip(0, w.fall_speed)


game = Game()
game.run_lobby()