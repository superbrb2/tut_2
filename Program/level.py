import pygame, sys
from settings import tile_size
from support import import_csv_layout, import_cut_graphics
from tiles import StaticTile, Crate, Coin, Palm
from enemy import Enemy
from settings import tile_size, screen_width
from player import Player
from particles import ParticleEffect


if __name__ == '__main__':
    print('Run "main.py" Not this File')
    sys.exit()

class Level:
    def __init__(self,level_data,surface):
        # General setup
        self.display_surface = surface
        self.world_shift = 0

        # Terrain setup
        terrain_layout = import_csv_layout(level_data['terrain'])
        self.terrian_sprites = self.create_tile_group(terrain_layout,'terrain')

        # Grass setup 
        grass_layout = import_csv_layout(level_data['grass'])
        self.grass_sprites = self.create_tile_group(grass_layout,'grass')

        # Crates setup
        crate_layout = import_csv_layout(level_data['crates'])
        self.crate_sprites = self.create_tile_group(crate_layout,'crates')

        # Coins setup
        coin_layout = import_csv_layout(level_data['coins'])
        self.coin_sprites = self.create_tile_group(coin_layout,'coins')

        # Foreground palms
        fg_palm_layout = import_csv_layout(level_data['fg_palms'])
        self.fg_palm_sprites = self.create_tile_group(fg_palm_layout,'fg_palms')

        # Background palms
        bg_palm_layout = import_csv_layout(level_data['bg_palms'])
        self.bg_palm_sprites = self.create_tile_group(bg_palm_layout,'bg_palms')

        # Enemy
        enemy_layout = import_csv_layout(level_data['enemies'])
        self.enemy_sprites = self.create_tile_group(enemy_layout,'enemies')
        
        # Player
        player_layout = import_csv_layout(level_data['players'])
        self.player_sprites = self.create_tile_group(player_layout,'players')
        
        # dust
        self.dust_sprite = pygame.sprite.GroupSingle()
        
        
        # Group for all groups of tiles that can interact with the player
        self.hit_box_group = self.create_hitbox_group()
    
    def create_hitbox_group(self):
        sprite_group = pygame.sprite.Group()
        groups_to_add = [
            self.terrian_sprites,
            self.crate_sprites,
            self.enemy_sprites,
        ]
        
        for i in range(len(groups_to_add)):
            sprite_group.add(groups_to_add[i])
        return sprite_group

    def create_tile_group(self,layout,type):
        sprite_group = pygame.sprite.Group()
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                if val != '-1':
                    x = col_index * tile_size
                    y = row_index * tile_size

                    if type == 'terrain':
                        terrain_tile_list = import_cut_graphics('graphics/terrain/terrain_tiles.png')
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(tile_size,x,y,tile_surface)
                        
                    if type == 'grass':
                        grass_tile_list = import_cut_graphics('graphics/decoration/grass/grass.png')
                        tile_surface = grass_tile_list[int(val)]
                        sprite = StaticTile(tile_size,x,y,tile_surface)

                    if type == 'crates':
                        sprite = Crate(tile_size,x,y)

                    if type == 'coins':
                        if val == '0': sprite = Coin(tile_size,x,y,'graphics/coins/gold')
                        if val == '1': sprite = Coin(tile_size,x,y,'graphics/coins/silver')

                    if type == 'fg_palms':
                        if val == '2': sprite = Palm(tile_size,x,y,'graphics/terrain/palm_small',38)
                        if val == '3': sprite = Palm(tile_size,x,y,'graphics/terrain/palm_large',66)
                    
                    if type == 'bg_palms':
                        sprite = Palm(tile_size,x,y,'graphics/terrain/palm_bg',64)

                    if type == 'enemies':
                        sprite = Enemy(tile_size,x,y)

                    if type == 'players':
                        self.player = Player((x,y),self.display_surface)
                        sprite_group.add(self.player)
                        return sprite_group
                    
                    sprite_group.add(sprite)

        return sprite_group

    
    def scroll_x(self):
        self.player.total_moved += (self.world_shift*-1) + (self.player.direction.x * self.player.speed)
        # self.player = self.player.sprite
        self.player_x = self.player.rect.centerx 
        direction_x = self.player.direction.x            
    
        if self.player_x < screen_width / 4 and direction_x < 0:
            self.world_shift = 8
            self.player.speed = 0
        elif self.player_x > screen_width - (screen_width / 4) and direction_x > 0:
            self.world_shift = -8
            self.player.speed = 0 
        else:
            self.world_shift = 0
            self.player.speed = 8
        
        # falling off back of level
        if self.player.total_moved < 0:
            self.world_shift = 0
            self.player.speed = 8
        if self.player.total_moved <= -312 and self.player.direction.x != 1:
            self.player.speed = 0
            self.world_shift = 0
    
    def player_horizontal_movement_collision(self):
        self.player.rect.x += self.player.direction.x * self.player.speed

        for sprite in self.hit_box_group.sprites():
            if sprite.rect.colliderect(self.player.rect):
                if self.player.direction.x < 0:
                    self.player.rect.left = sprite.rect.right
                    self.player.on_left = True
                    self.current_x = self.player.rect.left
                elif self.player.direction.x > 0:
                    self.player.rect.right = sprite.rect.left
                    self.player.on_right = True
                    self.current_x = self.player.rect.right
        
        if self.player.on_left and (self.player.rect.left < self.current_x or self.player.direction.x >= 0):
            self.player.on_left = False
        if self.player.on_right and (self.player.rect.right > self.current_x or self.player.direction.x <= 0):
            self.player.on_right = False
            
            
    def vertical_movement_collision(self):
        # self.player = self.player.sprite
        self.player.apply_gravity()  
        
        hit_flag = False
        for sprite in self.hit_box_group.sprites():
            if sprite.rect.colliderect(self.player.rect):   
                hit_flag = True         
                if self.player.direction.y > 0:
                    self.player.rect.bottom = sprite.rect.top
                    self.player.direction.y = 0
                    self.player.on_ground = True
                    
                elif self.player.direction.y < 0:
                    self.player.rect.top = sprite.rect.bottom
                    self.player.direction.y = 0
                    self.player.on_ceiling = True 
        # Still in air

        if not hit_flag:
            self.player.on_ground = False
            self.player.on_ceiling = False

                
        
        '''
        if self.player.on_ground and self.player.direction.y < 0 or self.player.direction.y > 0:
            self.player.on_ground = False

        if self.player.on_ceiling and self.player.direction.y > 0 and self.player.direction.y < 0:
            self.player.on_ceiling = False   
        '''
        
        
    def create_jump_particles(self,pos):
        if self.player_on_ground and not self.player.on_ground and not self.dust_sprite.sprites():
            if self.player.facing_right:
                offset = pygame.math.Vector2(10,15)
            else:
                offset = pygame.math.Vector2(-10,15)

            self.jump_paricle_sprite = ParticleEffect(self.player.rect.midbottom - offset,'jump')
            self.dust_sprite.add(self.jump_paricle_sprite)
            
    def get_player_on_ground(self):
        if self.player.on_ground:
            self.player_on_ground = True
        else:
            self.player_on_ground = False
    
    def create_landing_dust(self):
        if not self.player_on_ground and self.player.on_ground and not self.dust_sprite.sprites():
            if self.player.facing_right:
                offset = pygame.math.Vector2(10,15)
            else:
                offset = pygame.math.Vector2(-10,15)

            fall_dust_particle = ParticleEffect(self.player.rect.midbottom - offset,'land')
            self.dust_sprite.add(fall_dust_particle)

    def run(self):
        # Run the game

        # Background palms
        self.bg_palm_sprites.update(self.world_shift)
        self.bg_palm_sprites.draw(self.display_surface)

        # Terrain
        self.terrian_sprites.draw(self.display_surface)
        self.terrian_sprites.update(self.world_shift)

        # Enemy 
        self.enemy_sprites.update(self.world_shift)
        self.enemy_sprites.draw(self.display_surface)
        
        # Crates
        self.crate_sprites.update(self.world_shift)
        self.crate_sprites.draw(self.display_surface)
        
        # Grass
        self.grass_sprites.draw(self.display_surface)   
        self.grass_sprites.update(self.world_shift)

        # Foreground palms
        self.fg_palm_sprites.update(self.world_shift)
        self.fg_palm_sprites.draw(self.display_surface)

        # Coins
        self.coin_sprites.update(self.world_shift)
        self.coin_sprites.draw(self.display_surface)
        
        # Player
        self.player_horizontal_movement_collision()
        self.get_player_on_ground()
        self.vertical_movement_collision()
        self.create_landing_dust()
        self.create_jump_particles(self.player.rect.center)
        self.scroll_x()
        self.player.update()
        # self.player_sprites.draw(self.display_surface)
        
        # Dust       
        self.dust_sprite.update(self.world_shift)
        self.dust_sprite.draw(self.display_surface)

    