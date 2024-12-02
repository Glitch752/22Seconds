import pygame
import os
from typing import Self
from audio import SoundType
from game import Game
from game_scene import GameScene
from constants import TILE_SIZE
from game_scene.playing import draw_currency
from graphics import big_font_render, get_height, get_width, normal_font_render
from inputs import InputType, Inputs
from ui import Button
from items import Item

class InShopScene(GameScene):
    def __init__(self: Self, game: Game):
        super().__init__(game, "shop")
        self.shop_buttons = [
            Button(f"Buy Carrot Seed - {Item.CARROT_SEEDS.shop_data.buy_price}c", get_width() // 2, get_height() // 2, self.buy_item, (Item.CARROT_SEEDS,)),
            Button(f"Buy Onion Seed - {Item.ONION_SEEDS.shop_data.buy_price}c", get_width() // 2, get_height() // 2 + 40, self.buy_item, (Item.ONION_SEEDS,)),
            Button(f"Buy Wheat Seed - {Item.WHEAT_SEEDS.shop_data.buy_price}c", get_width() // 2, get_height() // 2 + 80, self.buy_item, (Item.WHEAT_SEEDS,)),
            Button(f"Buy 5 Walls - {Item.WALL.shop_data.buy_price}c", get_width() // 2, get_height() // 2 + 120, self.buy_item, (Item.WALL,)),
            Button(f"Buy a Bigger Farm - 1,500c", get_width() // 2, get_height() // 2 + 160, self.try_to_win_lmao, ()),
            Button(f"Exit Shop", get_width() // 2, get_height() // 2 + 240, self.exit_shop, ()),
        ]
    
    def buy_item(self, item: Item, received_quantity=1):
        player = self.game.player
        if player.currency >= (price := item.shop_data.buy_price):
            player.currency -= price
            player.items[item] += received_quantity
            
            self.game.audio_manager.play_sound(SoundType.BUY_ITEM)
        else:
            self.game.audio_manager.play_sound(SoundType.NO_MONEY)

    def try_to_win_lmao(self):
        from game_scene.outro_cutscene import OutroCutsceneScene
        player = self.game.player
        if player.currency >= 1500:
            self.game.audio_manager.play_sound(SoundType.BUY_ITEM)
            self.game.update_scene(OutroCutsceneScene(self.game))
        else:
            self.game.audio_manager.play_sound(SoundType.NO_MONEY)

    def exit_shop(self):
        self.game.enter_playing_scene()
    
    def enter(self: Self):
        self.game.audio_manager.play_shop_track()
        
        self.game.player.sell_items()
        
        sounds = self.game.player.profit // 10 + 1
        for i in range(sounds):
            self.game.audio_manager.play_sound(SoundType.BUY_ITEM, i * 100)

    def draw(self: Self, win: pygame.Surface, inputs: Inputs):
        win.fill('#bbff70')
        
        t = pygame.time.get_ticks() // 50
        t %= TILE_SIZE
        for x in range(get_width() // TILE_SIZE + 1):
            for y in range(get_height() // TILE_SIZE + 1):
                if (x + y) % 2 == 0:
                    pygame.draw.rect(win, '#abef70', (x * TILE_SIZE - t, y * TILE_SIZE - t, TILE_SIZE, TILE_SIZE))
        
        player = self.game.player
        win.blit(t := big_font_render("Shop", 'black'), (get_width() // 2 - t.get_width() // 2, 25))
        y = 85
        win.blit(t := normal_font_render(f"Carrots Sold ({Item.CARROT.shop_data.sell_price}c per): {player.get_sold_sold_agaaghhhh(Item.CARROT)}", 'black'), (get_width() // 2 - t.get_width() // 2, y))
        y += t.get_height()
        win.blit(t := normal_font_render(f"Onions Sold ({Item.ONION.shop_data.sell_price}c per): {player.get_sold_sold_agaaghhhh(Item.ONION)}", 'black'), (get_width() // 2 - t.get_width() // 2, y))
        y += t.get_height()
        win.blit(t := normal_font_render(f"Wheat Sold ({Item.WHEAT.shop_data.sell_price}c per): {player.get_sold_sold_agaaghhhh(Item.WHEAT)}", 'black'), (get_width() // 2 - t.get_width() // 2, y))
        y += t.get_height()
        win.blit(t := normal_font_render(f"Profit: {player.profit}", 'black'), (get_width() // 2 - t.get_width() // 2, y))
        
        draw_currency(win, player)

        # TODO: Cards instead of buttons
        for b in self.shop_buttons:
            b.draw(win)
    
    def event_input(self: Self, type: InputType):
        if type == InputType.CLICK_DOWN:
            mx, my = pygame.mouse.get_pos()
            for b in self.shop_buttons:
                b.on_click(mx, my)
            return

        if type == InputType.CANCEL:
            self.exit_shop()
    
    def update(self: Self, inputs: Inputs, dt: float):
        mx, my = pygame.mouse.get_pos()
        for b in self.shop_buttons:
            b.check_hover(mx, my)