import math
import random
import time

import config

import pygame
from pygame.locals import Rect, K_LEFT, K_RIGHT


class Basic:
    def __init__(self, color: tuple, speed: int = 0, pos: tuple = (0, 0), size: tuple = (0, 0)):
        self.color = color
        self.rect = Rect(pos[0], pos[1], size[0], size[1])
        self.center = (self.rect.centerx, self.rect.centery)
        self.speed = speed
        self.start_time = time.time()
        self.dir = 270

    def move(self):
        dx = math.cos(math.radians(self.dir)) * self.speed
        dy = -math.sin(math.radians(self.dir)) * self.speed
        self.rect.move_ip(dx, dy)
        self.center = (self.rect.centerx, self.rect.centery)

class Item(Basic):  # 아이템 클래스
    def __init__(self, pos: tuple):
        self.effect = random.choice(["red", "blue"])
        color = config.item_colors[self.effect]
        super().__init__(color, 2, pos, config.item_size)
    def draw(self, surface):
        pygame.draw.ellipse(surface, self.color, self.rect)
        
class Block(Basic):
    active_blocks = 0                       # 활성화된 블록의 수를 관리(alive()에서 쓰임)

    def __init__(self, color: tuple, pos: tuple = (0,0), alive = True):
        super().__init__(color, 0, pos, config.block_size)
        self.pos = pos
        self.alive = alive
        if self.alive:
            Block.active_blocks += 1        # 블럭 생성 시 1씩 추가

    def draw(self, surface) -> None:
        pygame.draw.rect(surface, self.color, self.rect)
    
    def collide(self):
        if self.alive:
            self.alive = False
            Block.active_blocks -= 1        #블럭 충돌 시 1씩 감소


class Paddle(Basic):
    def __init__(self):
        super().__init__(config.paddle_color, 0, config.paddle_pos, config.paddle_size)
        self.start_pos = config.paddle_pos
        self.speed = config.paddle_speed
        self.cur_size = config.paddle_size

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

    def move_paddle(self, event: pygame.event.Event):
        if event.key == K_LEFT and self.rect.left > 0:
            self.rect.move_ip(-self.speed, 0)
        elif event.key == K_RIGHT and self.rect.right < config.display_dimension[0]:
            self.rect.move_ip(self.speed, 0)


class Ball(Basic):
    def __init__(self, pos: tuple = config.ball_pos):
        super().__init__(config.ball_color, config.ball_speed, pos, config.ball_size)
        self.power = 1
        self.dir = 90 + random.randint(-45, 45)

    def draw(self, surface):
        pygame.draw.ellipse(surface, self.color, self.rect)

    def collide_block(self, blocks, items):
        for block in blocks[:]:
            if block.alive and self.rect.colliderect(block.rect):
                block.collide()
                blocks.remove(block)                    # 충돌 시 블럭 삭제
                self.dir = 360 - self.dir               # 충돌 후 반대 방향으로 날아감
                if random.random() < config.item_drop_prob:
                    items.append(Item(block.rect.center))   

    def collide_paddle(self, paddle: Paddle) -> None:
        if self.rect.colliderect(paddle.rect):
            self.dir = 360 - self.dir + random.randint(-5, 5)

    def hit_wall(self):
        if self.rect.left <= 0 or self.rect.right >= config.display_dimension[0]:   # 좌우 벽 충돌
            self.dir = 180 - self.dir
        if self.rect.top <= 0:                                                      # 상단 벽 충돌
            self.dir = 360 - self.dir
        
    def alive(self) -> bool:                                        # 게임이 clear된 이후에 Life 감소를 막기 위해 active_blocks 도입
        if self.rect.top >= config.display_dimension[1]:    # 공이 화면 아래로 떨어지면 Life 감소
            return False
        return True