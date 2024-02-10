from random import randint

import pygame

# Инициализация PyGame:
pygame.init()

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 10

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()

# Словарь нажатая клавиша: ожидаемое направление (dx, dy)
DICT_KEY = {pygame.K_UP: UP,
            pygame.K_DOWN: DOWN,
            pygame.K_LEFT: LEFT,
            pygame.K_RIGHT: RIGHT}


class GameObject:
    """Базовый класс игровых объектов"""

    body_color = BOARD_BACKGROUND_COLOR

    def __init__(self):
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    def draw(self):
        """Метод рисования должен быть определен в наследуемом классе"""
        raise NotImplementedError(
            f'draw() method not defined in {self.__class__.__name__}'
        )

    def draw_rect(self, surface):
        """Базовый метод рисования объекта для дочерних классов"""
        rect = pygame.Rect(
            (self.position[0], self.position[1]),
            (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Класс Apple"""

    body_color = APPLE_COLOR

    def __init__(self):
        super().__init__()
        self.body_color = Apple.body_color
        self.position = self.randomize_position()

    def draw(self, surface):
        """Рисование объекта Apple"""
        super().draw_rect(surface)

    def randomize_position(self):
        """Получение случайных координат, упакованных в кортеж для Apple"""
        x = GRID_SIZE * randint(0, SCREEN_WIDTH // GRID_SIZE - 1)
        y = GRID_SIZE * randint(0, SCREEN_HEIGHT // GRID_SIZE - 1)
        return (x, y)


class Snake(GameObject):
    """Управляемый игроком объект Snake"""

    body_color = SNAKE_COLOR

    def __init__(self, length=1, direction=RIGHT, next_direction=RIGHT):
        super().__init__()
        self.length = length
        self.positions = [self.position]
        self.last = None
        self.direction = direction
        self.next_direction = next_direction
        self.body_color = Snake.body_color

    def draw(self, surface):
        """Рисование объекта Snake"""
        for self.position in self.positions:
            super().draw_rect(surface)
        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(
                (self.last[0], self.last[1]),
                (GRID_SIZE, GRID_SIZE)
            )
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, last_rect)

    def move(self):
        """Перемещение объекта Snake"""
        direction = (self.direction[0] * GRID_SIZE,
                     self.direction[1] * GRID_SIZE)
        self.last = self.positions[self.length - 1]
        new_head_position = (tuple(map(sum, zip(self.get_head_position(),
                                                direction))))
        if new_head_position in self.positions:
            self.reset()
            return
        elif new_head_position[0] > (SCREEN_WIDTH - GRID_SIZE):
            x = 0
            y = new_head_position[1]
            new_head_position = (x, y)
        elif new_head_position[0] < 0:
            x = SCREEN_WIDTH - GRID_SIZE
            y = new_head_position[1]
            new_head_position = (x, y)
        elif new_head_position[1] > (SCREEN_HEIGHT - GRID_SIZE):
            x = new_head_position[0]
            y = 0
            new_head_position = (x, y)
        elif new_head_position[1] < 0:
            x = new_head_position[0]
            y = SCREEN_HEIGHT - GRID_SIZE
            new_head_position = (x, y)

        self.positions.insert(0, new_head_position)
        self.positions.pop()

    def get_head_position(self):
        """Возвращает позицию головы змейки в виде кортежа"""
        return self.positions[0]

    def reset(self):
        """Сброс змейки в исходное состояние"""
        self.__init__(1, RIGHT, None)
        self.next_direction = RIGHT
        screen.fill(BOARD_BACKGROUND_COLOR)

    def update_direction(self):
        """Обновление направления движения"""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None


def handle_keys(game_object):
    """Обработка нажатий клавиш или кнопки закрытия окна"""
    global SPEED
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            # Проверка условия нажата ли кнопка изменения направления
            if event.key in DICT_KEY:
                # Проверка на попытку разворота на 180
                for i, k in zip(DICT_KEY.get(event.key),
                                game_object.direction):
                    game_object.next_direction = (
                        DICT_KEY.get(event.key) if (i + k) else None)
            # Изменение скорости змейки при нажатии кнопок + / -
            elif event.key == pygame.K_MINUS and SPEED > 1:
                SPEED -= 1
            elif event.key == pygame.K_PLUS or pygame.K_KP_PLUS:
                SPEED += 1


def main():
    """Основной цикл"""
    apple = Apple()
    snake = Snake()
    while True:
        if apple.position == snake.get_head_position():
            snake.positions.append(snake.last)
            snake.length += 1
            # Apple не может появиться в том месте, где отрисована змейка
            while apple.position in snake.positions:
                # Получение новых рандомных координат для Apple
                apple.position = apple.randomize_position()

        apple.draw(screen)
        handle_keys(snake)
        snake.update_direction()
        snake.move()
        snake.draw(screen)
        pygame.display.update()
        clock.tick(SPEED)


if __name__ == '__main__':
    main()
