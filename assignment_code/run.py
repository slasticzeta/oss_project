import sys
from implements import Basic, Block, Paddle, Ball, Item
import config

import pygame
from pygame.locals import QUIT, Rect, K_ESCAPE, K_SPACE


pygame.init()
pygame.key_set_repeat(3, 3)
surface = pygame.display.set_mode(config.display_dimension)

fps_clock = pygame.time.Clock()

paddle = Paddle()
ball1 = Ball()
BLOCKS = []
ITEMS = []
BALLS = [ball1]
life = config.life
start = False


def create_blocks():
    for i in range(config.num_blocks[0]):
        for j in range(config.num_blocks[1]):
            x = config.margin[0] + i * (config.block_size[0] + config.spacing[0])
            y = (
                config.margin[1]
                + config.scoreboard_height
                + j * (config.block_size[1] + config.spacing[1])
            )
            color_index = j % len(config.colors)
            color = config.colors[color_index]
            block = Block(color, (x, y))
            BLOCKS.append(block)


def tick():
    global life, BLOCKS, ITEMS, BALLS, paddle, ball1, start

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == K_ESCAPE:  # ESC 키가 눌렸을 때
                pygame.quit()
                sys.exit()
            if event.key == K_SPACE:  # space키가 눌리면 게임 시작
                start = True
            paddle.move_paddle(event)

    for ball in BALLS:
        if start:
            ball.move()
        else:
            ball.rect.centerx = paddle.rect.centerx
            ball.rect.bottom = paddle.rect.top

        ball.collide_block(BLOCKS, ITEMS)
        ball.collide_paddle(paddle)
        ball.hit_wall()
        if not ball.alive():
            BALLS.remove(ball)

    # 아이템 이동 및 충돌 처리
    for item in ITEMS[:]:
        item.move()
        if item.rect.top > config.display_dimension[1]:
            ITEMS.remove(item)  # 화면 아래로 사라진 아이템 제거
        elif item.rect.colliderect(paddle.rect):
            # 아이템 충돌 처리
            if item.effect == "red":  # 빨간색 공 아이템
                BALLS.append(Ball((paddle.rect.centerx, paddle.rect.top)))  # 새로운 공 추가
            ITEMS.remove(item)  # 아이템 제거


def main():
    global life, BLOCKS, ITEMS, BALLS, paddle, ball1, start

    my_font = pygame.font.SysFont(None, 50)
    mess_clear = my_font.render("Cleared!", True, config.colors[2])
    mess_over = my_font.render("Game Over!", True, config.colors[2])
    create_blocks()

    while True:
        tick()
        surface.fill((0, 0, 0))
        paddle.draw(surface)

        for block in BLOCKS:
            block.draw(surface)

        cur_score = config.num_blocks[0] * config.num_blocks[1] - len(BLOCKS)

        score_txt = my_font.render(f"Score : {cur_score * 10}", True, config.colors[2])
        life_font = my_font.render(f"Life: {life}", True, config.colors[0])

        surface.blit(score_txt, config.score_pos)
        surface.blit(life_font, config.life_pos)

        if len(BALLS) == 0:
            if life > 1:
                life -= 1
                ball1 = Ball()
                BALLS = [ball1]
                start = False
            else:
                surface.blit(mess_over, (200, 300))
        elif all(block.alive == False for block in BLOCKS):
            surface.blit(mess_clear, (200, 400))
        else:
            for ball in BALLS:
                ball.draw(surface)
            for item in ITEMS:
                item.draw(surface)

        pygame.display.update()
        fps_clock.tick(config.fps)


if __name__ == "__main__":
    main()
