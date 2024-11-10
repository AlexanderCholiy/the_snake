from random import randint
from typing import Optional

import pygame

from app.read_game_record import read_game_record
from app.write_game_result import write_game_result

# Константы с типом данных:
POINTER_POSITION = tuple[int, int]
POINTER_COLOR = tuple[int, int, int]

# Константы для размеров поля, сетки и центра экрана:
SCREEN_WIDTH: int = 640
SCREEN_HEIGHT: int = 480
SCREEN_CENTER_POSITION: POINTER_POSITION = (
    SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
)
GRID_SIZE: int = 20
GRID_WIDTH: int = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT: int = SCREEN_HEIGHT // GRID_SIZE
TOTAL_CELLS = GRID_WIDTH * GRID_HEIGHT

# Направления движения:
UP: POINTER_POSITION = (0, -1)
DOWN: POINTER_POSITION = (0, 1)
LEFT: POINTER_POSITION = (-1, 0)
RIGHT: POINTER_POSITION = (1, 0)

# Константы цветов:
BOARD_BACKGROUND_COLOR: POINTER_COLOR = (51, 51, 51)
BORDER_COLOR: POINTER_COLOR = (204, 204, 204)
GAME_OBJECT_COLOR: POINTER_COLOR = (0, 0, 0)
APPLE_COLOR: POINTER_COLOR = (220, 20, 60)
SNAKE_COLOR: POINTER_COLOR = (34, 139, 34)
VICTORY_TEXT_COLOR: POINTER_COLOR = (255, 0, 255)
RECORD_TEXT_COLOR: POINTER_COLOR = (255, 255, 0)

# Скорость движения змейки:
SPEED: int = 20

# Задержка уведомлений (миллисекунды):
NOTIFICATION_DELAY: int = 3000

# Словарь с возможными движениями змейки:
GAME_CONTROL = {
    (UP, pygame.K_LEFT): LEFT,
    (UP, pygame.K_RIGHT): RIGHT,
    (DOWN, pygame.K_LEFT): LEFT,
    (DOWN, pygame.K_RIGHT): RIGHT,
    (LEFT, pygame.K_UP): UP,
    (LEFT, pygame.K_DOWN): DOWN,
    (RIGHT, pygame.K_UP): UP,
    (RIGHT, pygame.K_DOWN): DOWN,
}

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
game_record = read_game_record()
pygame.display.set_caption(
    'Snake (to exit press ❌). '
    f'Speed {SPEED}. Record {game_record} apples!'
)

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """
    Базовый класс, от которого наследуются другие игровые объекты.
    Он содержит общие атрибуты игровых объектов — позицию (position)
    и цвет объекта (body_color), который задаётся RGB-значением. Этот же класс
    содержит и заготовку метода для отрисовки объекта на игровом поле — draw.
    """

    def __init__(
        self,
        body_color: POINTER_COLOR = GAME_OBJECT_COLOR,
        position: POINTER_POSITION = SCREEN_CENTER_POSITION
    ):
        """
        Parameters
        ----------
        body_color : tuple[int, int, int]
            Цвет объекта.
        position : tuple[int, int]
            Позиция объекта на игровом поле. По умолчанию она инициализируется
            как центральная точка экрана.
        """
        self.position = position
        self.body_color = body_color

    def draw(self) -> None:
        """
        Абстрактный метод, который предназначен для переопределения в дочерних
        классах. Этот метод должен определять, как объект будет отрисовываться
        на экране.
        """


class Apple(GameObject):
    """
    Дочерний класс, унаследованный от GameObject, описывающий яблоко и действия
    с ним. Яблоко должно отображаться в случайных клетках игрового поля.
    """

    def __init__(
        self,
        body_color: POINTER_COLOR = APPLE_COLOR,
        occupied_positions: Optional[list[POINTER_POSITION]] = None
    ):
        """
        Parameters
        ----------
        body_color : tuple[int, int, int]
            Цвет яблока. В данном случае задаётся RGB-значением
        position : tuple[int, int]
            Позиция яблока на игровом поле. Яблоко появляется в случайном месте
            на игровом поле.
        occupied_positions : list[tuple[int, int]]
            Список позиций сегментов других объектов, чтобы исключить их из
            возможных позиций яблока.
        """
        super().__init__(body_color)
        self.randomize_position(occupied_positions or [SCREEN_CENTER_POSITION])

    def randomize_position(
        self, occupied_positions: list[POINTER_POSITION]
    ) -> None:
        """
        Устанавливает случайное положение яблока на игровом поле — задаёт
        атрибуту position новое значение. Координаты выбираются так, чтобы
        яблоко оказалось в пределах игрового поля.
        """
        # Убедимся, что координаты не превышают границы экрана и уберём
        # возможность появления яблока прямо на змейке.
        while True:
            random_x_value = randint(0, GRID_WIDTH - 1) * GRID_SIZE
            random_y_value = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            new_position = (random_x_value, random_y_value)
            if new_position not in occupied_positions:
                self.position = new_position
                break

    def draw(self) -> None:
        """Отрисовывает яблоко на игровой поверхности."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """
    Змейка — это список координат, каждый элемент списка соответствует
    отдельному сегменту тела змейки. Атрибуты и методы класса обеспечивают
    логику движения, отрисовку, обработку событий (нажата клавиша) и другие
    аспекты поведения змейки в игре.
    """

    def __init__(
        self,
        body_color: POINTER_COLOR = SNAKE_COLOR
    ):
        """
        Parameters
        ----------
        body_color: tuple[int, int, int]
            Цвет змейки. Задаётся RGB-значением (по умолчанию — зелёный:
            (0, 255, 0)).
        positions : list[tuple[[int, int]]]
            Cписок, содержащий позиции всех сегментов тела змейки. Начальная
            позиция — центр экрана.
        length : int
            Длина змейки. По умолчанию змейка имеет длину 1.
        direction: tuple[int, int]
            Направление движения змейки. По умолчанию змейка движется вправо.
        next_direction: tuple[int, int]
            Следующее направление движения, которое будет применено после
            обработки нажатия клавиши.
        last: tuple[int, int]
            Атрибут используется для хранения позиции последнего сегмента
            змейки перед тем, как он исчезнет (при движении змейки). Это
            необходимо для «стирания» этого сегмента с игрового поля, чтобы
            змейка визуально двигалась.
        """
        self.body_color = body_color
        self.positions: list[POINTER_POSITION] = [SCREEN_CENTER_POSITION]
        self.length: int = 1
        self.direction: POINTER_POSITION = RIGHT
        self.next_direction: Optional[POINTER_POSITION] = None
        self.last: Optional[POINTER_POSITION] = None
        super().__init__(
            body_color=body_color,
            position=self.get_head_position()
        )

    def update_direction(self) -> None:
        """Метод обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction

    def move(self) -> None:
        """
        Метод обновляет позицию змейки (координаты каждой секции), добавляя
        новую голову в начало списка positions и удаляя последний элемент, если
        длина змейки не увеличилась.
        """
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        # Вычисление новой позиции головы с учётом размеров сетки.
        new_head_x, new_head_y = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        )
        new_head_position = (new_head_x, new_head_y)

        self.positions.insert(0, new_head_position)

        if self.positions[self.length:]:
            self.last = self.positions.pop()

    def draw(self) -> None:
        """Отрисовывает змейку на экране, затирая след."""
        for position in self.positions:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        head_rect = pygame.Rect(
            self.get_head_position(), (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self) -> POINTER_POSITION:
        """
        Метод возвращает текущее положение головы змейки (первый элемент в
        списке positions).
        """
        return self.positions[0]

    def reset(self) -> None:
        """Метод сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [SCREEN_CENTER_POSITION]


def handle_keys(game_object) -> None:
    """
    Функция обрабатывает нажатия клавиш, чтобы изменить направление движения
    змейки.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            write_game_result(snake_lenght=game_object.length)
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            new_direction = GAME_CONTROL.get(
                (game_object.direction, event.key)
            )
            if new_direction and game_object.direction != new_direction:
                game_object.next_direction = new_direction


def main():
    """
    Основной игровой цикл.

    Raises
    ------
    SystemExit
        Победа, если длина змейки равна общему количеству клеток на поле.
    """
    # Инициализация PyGame:
    pygame.init()
    font = pygame.font.SysFont('Arial', 48)

    snake = Snake()
    apple = Apple(occupied_positions=snake.positions)

    while True:
        # Очистим экран, заполнив его фоновым цветом (BOARD_BACKGROUND_COLOR).
        screen.fill(BOARD_BACKGROUND_COLOR)

        # Регулируем скорость движения змейки.
        clock.tick(SPEED)

        # Тут опишите основную логику игры.
        apple.draw()
        snake.draw()

        # Обновление состояний объектов: змейка обрабатывает нажатия клавиш
        # и двигается в соответствии с выбранным направлением.
        handle_keys(snake)
        snake.update_direction()

        # Событие «змейка съела яблоко» — состояние, когда координаты головы
        # змейки совпали с координатами яблока.
        if snake.get_head_position() == apple.position:
            snake.length += 1

            # Изменим координаты яблока.
            apple.randomize_position(snake.positions)

        # Событие столкновения змейки с собой (если столкновение, сброс игры
        # при помощи метода reset()).
        elif snake.get_head_position() in snake.positions[1:]:
            game_record = read_game_record()
            write_game_result(snake_lenght=snake.length)

            if snake.length > game_record:
                victory_text = font.render(
                    f'New record {snake.length} apples!', True,
                    RECORD_TEXT_COLOR
                )
                text_rect = victory_text.get_rect(
                    center=SCREEN_CENTER_POSITION
                )
                screen.blit(victory_text, text_rect)
                pygame.display.update()
                pygame.time.wait(NOTIFICATION_DELAY)

            snake.reset()

        # Теоретическая проверка на заполнение змейкой всего поля)
        if snake.length == TOTAL_CELLS:
            write_game_result(snake_lenght=snake.length)
            victory_text = font.render('Victory!', True, VICTORY_TEXT_COLOR)
            text_rect = victory_text.get_rect(center=SCREEN_CENTER_POSITION)
            screen.blit(victory_text, text_rect)

            pygame.display.update()
            pygame.time.wait(NOTIFICATION_DELAY)
            pygame.quit()
            raise SystemExit

        # Обновляем позицию змейки.
        snake.move()

        # Обновление экрана.
        pygame.display.update()


if __name__ == '__main__':
    main()
