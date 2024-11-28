import pygame
import os
from typing import Self
from audio import SOUND_TYPE
from game import Game
from game_scene import GameScene
from constants import HEIGHT, TILE_SIZE, WIDTH
from game_scene.playing import draw_currency
from graphics import big_font_render, normal_font_render
from inputs import InputType, Inputs
from ui import Button
from items import item_prices, ITEM_TYPE

class InShopScene(GameScene):
    def __init__(self: Self, game: Game):
        super().__init__(game)
        self.shop_buttons = [
            Button(f"Buy Carrot Seed - {item_prices[ITEM_TYPE.CARROT_SEEDS]}c", WIDTH // 2, HEIGHT // 2, self.buy_item, (ITEM_TYPE.CARROT_SEEDS)),
            Button(f"Buy Onion Seed - {item_prices[ITEM_TYPE.ONION_SEEDS]}c", WIDTH // 2, HEIGHT // 2 + 40, self.buy_item, (ITEM_TYPE.ONION_SEEDS)),
            Button(f"Buy Wheat Seed - {item_prices[ITEM_TYPE.WHEAT_SEEDS]}c", WIDTH // 2, HEIGHT // 2 + 80, self.buy_item, (ITEM_TYPE.WHEAT_SEEDS)),
            Button(f"Buy 5 Walls - {item_prices[ITEM_TYPE.WALL]}c", WIDTH // 2, HEIGHT // 2 + 120, self.buy_item, (ITEM_TYPE.WALL)),
            Button(f"Idk move our or something - 1,000c", WIDTH // 2, HEIGHT // 2 + 160, self.try_to_win_lmao, ()),
            Button(f"Exit Shop", WIDTH // 2, HEIGHT // 2 + 240, self.exit_shop, ()),
        ]
    
    def buy_item(self, item, received_quantity=1):
        player = self.game.player
        if player.currency >= (price := item_prices[item]):
            player.currency -= price
            player.items[item] += received_quantity
            
            self.game.audio_manager.play_sound(SOUND_TYPE.BUY_ITEM)
        else:
            self.game.audio_manager.play_sound(SOUND_TYPE.NO_MONEY)

    def try_to_win_lmao(self):
        from game_scene.outro_cutscene import OutroCutsceneScene
        player = self.game.player
        if player.currency >= 1000:
            self.game.audio_manager.play_sound(SOUND_TYPE.BUY_ITEM)
            self.game.update_scene(OutroCutsceneScene(self.game))
        else:
            self.game.audio_manager.play_sound(SOUND_TYPE.NO_MONEY)

    def exit_shop(self):
        self.game.enter_playing_scene()
    
    def enter(self: Self):
        self.game.audio_manager.play_shop_track()
        
        self.game.player.sell_items()
        
        sounds = self.game.player.profit // 10 + 1
        for i in range(sounds):
            self.game.audio_manager.play_sound(SOUND_TYPE.BUY_ITEM, i * 100)

    def draw(self: Self, win: pygame.Surface):
        win.fill('#bbff70')
        
        t = pygame.time.get_ticks() // 50
        t %= TILE_SIZE
        for x in range(WIDTH // TILE_SIZE + 1):
            for y in range(HEIGHT // TILE_SIZE + 1):
                if (x + y) % 2 == 0:
                    pygame.draw.rect(win, '#abef70', (x * TILE_SIZE - t, y * TILE_SIZE - t, TILE_SIZE, TILE_SIZE))
        
        player = self.game.player
        win.blit(t := big_font_render("Shop", 'black'), (WIDTH // 2 - t.get_width() // 2, 25))
        y = 85
        win.blit(t := normal_font_render(f"Carrots Sold ({item_prices[ITEM_TYPE.CARROT]}c per): {player.get_sold(ITEM_TYPE.CARROT)}", 'black'), (WIDTH // 2 - t.get_width() // 2, y))
        y += t.get_height()
        win.blit(t := normal_font_render(f"Onions Sold ({item_prices[ITEM_TYPE.ONION]}c per): {player.get_sold(ITEM_TYPE.ONION)}", 'black'), (WIDTH // 2 - t.get_width() // 2, y))
        y += t.get_height()
        win.blit(t := normal_font_render(f"Wheat Sold ({item_prices[ITEM_TYPE.WHEAT]}c per): {player.get_sold(ITEM_TYPE.WHEAT)}", 'black'), (WIDTH // 2 - t.get_width() // 2, y))
        y += t.get_height()
        win.blit(t := normal_font_render(f"Profit: {player.profit}", 'black'), (WIDTH // 2 - t.get_width() // 2, y))
        
        draw_currency()

        # TODO: Cards instead of buttons
        for b in self.shop_buttons:
            b.draw(win)
    
    def event_input(self: Self, type: InputType):
        if type == InputType.CLICK_DOWN:
            mx, my = pygame.mouse.get_pos()
            for b in self.shop_buttons:
                b.on_click(mx, my)
            return
        
    def enter(self: Self):
        for box in self.cutscene_text:
            self.game.dialogue.queue_dialogue(box)
        self.game.dialogue.on_confirm()
    
    def update(self: Self, inputs: Inputs, dt: float):
        mx, my = pygame.mouse.get_pos()
        for b in self.shop_buttons:
            b.check_hover(mx, my)