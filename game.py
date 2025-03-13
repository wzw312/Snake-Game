# 在文件顶部添加freetype模块导入
import pygame.freetype
import os
import sys
import pygame
import random

# 初始化 pygame
pygame.init()

# 获取资源路径（新增代码）
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# 修改后的资源加载（约28-35行）
font_path = resource_path("SimHei.ttf")
font_style = pygame.freetype.Font(font_path, 25)
score_font = pygame.freetype.Font(font_path, 35)

# 在音效加载代码块后添加（约35行附近）
try:
    # 使用新的路径获取方式
    eat_sound = pygame.mixer.Sound(resource_path("eat_sound.wav"))
    pygame.mixer.music.load(resource_path("background_music.wav"))
    # 新增播放控制 ↓↓↓
    pygame.mixer.music.play(-1)  # -1表示循环播放
    pygame.mixer.music.set_volume(0.5)  # 设置音量（0.0到1.0）
except pygame.error as e:
    print(f"音效加载失败: {e}")
    eat_sound = pygame.mixer.Sound(None)
    # 添加音乐加载失败处理 ↓↓↓
    pygame.mixer.music = None  # 标记音乐加载失败

def your_score(score):
    value, _ = score_font.render(f"你的得分: {score}", black)
    screen.blit(value, [0, 0])

def our_snake(snake_block, snake_list):
    for x in snake_list:
        pygame.draw.rect(screen, black, [x[0], x[1], snake_block, snake_block])

# 将以下函数定义移动到变量声明之后
# 原位置（约37-53行）移动到变量声明之后

# 设定屏幕大小和颜色
white = (255, 255, 255)
black = (0, 0, 0)
red = (213, 50, 80)
blue = (50, 153, 213)

# 创建屏幕
width = 600
height = 400

# 设置蛇的初始参数
snake_block = 10  # 现在这个变量在函数调用前定义
snake_speed = 5
clock = pygame.time.Clock()

# 现在定义 generate_food 函数（原位置在35行）
def generate_food():
    food_types = [
        {'color': (255, 215, 0), 'effect': 'score+1', 'glow': True},
        {'color': (255, 105, 180), 'effect': 'speed+2', 'glow': False},
        {'color': (0, 255, 127), 'effect': 'shrink', 'glow': True}
    ]
    return {
        'x': random.randint(0, (width // snake_block) - 1) * snake_block,
        'y': random.randint(0, (height // snake_block) - 1) * snake_block,
        **random.choice(food_types)
    }

# 在Pygame初始化后添加错误检测
if not pygame.get_init():
    print("Pygame初始化失败!")
    sys.exit(1)

# 修改屏幕初始化部分（约97-100行）
try:
    screen = pygame.display.set_mode((width, height))
except pygame.error as e:
    print(f"显示模式设置失败: {e}")
    pygame.quit()
    sys.exit()

# 在游戏主循环中添加异常捕获
def gameLoop():
    try:
        global snake_speed
        game_over = False
        game_close = False
    except Exception as e:
        print(f"游戏运行时错误: {e}")
        pygame.quit()
        raise

    # 初始化游戏状态
    x1, y1 = width / 2, height / 2
    x1_change = y1_change = 0
    snake_List = []
    Length_of_snake = 1
    current_food = generate_food()
    snake_speed = 5
    total_score = 0  # 新增累计计分变量

    while not game_over:
        screen.fill(blue)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x1_change = -snake_block
                    y1_change = 0
                elif event.key == pygame.K_RIGHT:
                    x1_change = snake_block
                    y1_change = 0
                elif event.key == pygame.K_UP:
                    y1_change = -snake_block
                    x1_change = 0
                elif event.key == pygame.K_DOWN:
                    y1_change = snake_block
                    x1_change = 0

        # 移动和碰撞检测
        x1 += x1_change
        y1 += y1_change
        if x1 < 0 or x1 >= width or y1 < 0 or y1 >= height:
            game_close = True

        # 精确碰撞检测（修复点）
        if x1 == current_food['x'] and y1 == current_food['y']:
            eat_sound.play()
            effect = current_food['effect']
            total_score += 1  # 无论食物效果如何，吃到就计分
            if effect == 'speed+2':
                snake_speed += 2
            elif effect == 'shrink':
                Length_of_snake = max(1, Length_of_snake - 1)
                # 立即缩短蛇身
                while len(snake_List) > Length_of_snake:
                    del snake_List[0]
            Length_of_snake += 1  # 每吃到一个食物，蛇身长度增加 1
            current_food = generate_food()

        # 更新蛇身
        snake_Head = [x1, y1]
        snake_List.append(snake_Head)
        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        # 碰撞自身检测
        if len(snake_List) > 1:
            for segment in snake_List[:-1]:
                if segment == snake_Head:
                    game_close = True

        # 绘制元素
        if current_food['glow']:
            glow_radius = int(5 * abs(pygame.time.get_ticks() % 1000 - 500) / 500)
            pygame.draw.circle(screen, (255, 255, 255),
                               (current_food['x'] + 5, current_food['y'] + 5), snake_block // 2 + glow_radius)
        pygame.draw.ellipse(screen, current_food['color'],
                            [current_food['x'], current_food['y'], snake_block, snake_block])

        our_snake(snake_block, snake_List)
        your_score(total_score)  # 显示累计得分
        pygame.display.update()
        clock.tick(snake_speed)

        # 游戏结束处理
        while game_close:
            screen.fill(blue)
            message, _ = font_style.render("你输了! 按 Q 退出 或 按 C 再来一次", red)
            screen.blit(message, [width / 6, height / 3])
            your_score(total_score)  # 显示累计得分
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        return gameLoop()

    # 替换所有退出点为以下形式
    pygame.quit()
    sys.exit(退出码)  # 0表示正常退出，非0表示异常


if __name__ == "__main__":
    try:
        gameLoop()
    except Exception as e:
        with open("error.log", "w") as f:
            f.write(str(e))
        pygame.quit()
        sys.exit(1)  # 确保所有退出都使用 sys.exit