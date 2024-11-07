# from random import choice, randint
from random import randint
from typing import Optional
import pygame

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
BOARD_BACKGROUND_COLOR = (51, 51, 51)

# Цвет границы ячейки
BORDER_COLOR = (204, 204, 204)

# Цвет яблока
APPLE_COLOR = (220, 20, 60)

# Цвет змейки
SNAKE_COLOR = (34, 139, 34)

# Скорость движения змейки:
SPEED = 10

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """
    Базовый класс, от которого наследуются другие игровые объекты.
    Он содержит общие атрибуты игровых объектов — позицию (position)
    и цвет объекта (body_color), который задаётся RGB-значением. Этот же класс
    содержит и заготовку метода для отрисовки объекта на игровом поле — draw.
    """

    def __init__(
        self,
        body_color: tuple[int, int, int] = (0, 0, 0),
        position: tuple[int, int] = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
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
        ...


class Apple(GameObject):
    """
    Дочерний класс, унаследованный от GameObject, описывающий яблоко и действия
    с ним. Яблоко должно отображаться в случайных клетках игрового поля.
    """

    def __init__(
        self,
        body_color: tuple[int, int, int] = (255, 0, 0),
        snake_positions: list[tuple[int, int]] = [
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        ]
    ):
        """
        Parameters
        ----------
        body_color : tuple[int, int, int]
            Цвет яблока. В данном случае задаётся RGB-значением
        position : tuple[int, int]
            Позиция яблока на игровом поле. Яблоко появляется в случайном месте
            на игровом поле.
        snake_positions : list[tuple[int, int]]
            Список позиций сегментов змейки, чтобы исключить их из возможных
            позиций яблока.
        """
        position = self.randomize_position(snake_positions)
        super().__init__(body_color, position)

    def randomize_position(
        self, snake_positions: list[tuple[int, int]]
    ) -> tuple[int, int]:
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
            if new_position not in snake_positions:
                return new_position

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
        length: int = 1,
        positions: list[tuple[int, int]] = [
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        ],
        direction: tuple[int, int] = RIGHT,
        next_direction: Optional[tuple[int, int]] = None,
        body_color: tuple[int, int, int] = (0, 255, 0),
        last: Optional[tuple[int, int]] = None
    ):
        """
        Parameters
        ----------
        length : int
            Длина змейки. По умолчанию змейка имеет длину 1.
        positions : list[tuple[[int, int]]]
            Cписок, содержащий позиции всех сегментов тела змейки. Начальная
            позиция — центр экрана.
        direction: tuple[int, int]
            Направление движения змейки. По умолчанию змейка движется вправо.
        next_direction: tuple[int, int]
            Следующее направление движения, которое будет применено после
            обработки нажатия клавиши.
        body_color: tuple[int, int, int]
            Цвет змейки. Задаётся RGB-значением (по умолчанию — зелёный:
            (0, 255, 0)).
        last: tuple[int, int]
            Атрибут используется для хранения позиции последнего сегмента
            змейки перед тем, как он исчезнет (при движении змейки). Это
            необходимо для «стирания» этого сегмента с игрового поля, чтобы
            змейка визуально двигалась.
        """
        self.length = length
        self.positions = positions
        self.direction = direction
        self.next_direction = next_direction
        self.body_color = body_color
        self.last = last
        super().__init__(body_color=body_color, position=positions[0])

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
        # Получение текущей головной позиции.
        current_head_position = self.get_head_position()
        dx, dy = self.direction
        # Вычисление новой позиции головы с учётом размеров сетки.
        new_head_x = (
            (current_head_position[0] + dx * GRID_SIZE) % SCREEN_WIDTH
        )
        new_head_y = (
            (current_head_position[1] + dy * GRID_SIZE) % SCREEN_HEIGHT
        )
        new_head_position = (new_head_x, new_head_y)

        # Обновление списка позиций.
        self.positions.insert(0, new_head_position)

        # Проверяется, превышает ли текущая длина змейки её максимальное
        # значение. Если да, последний элемент списка удаляется, имитируя
        # движение змейки. Если нет, это означает, что змейка только что съела
        # яблоко, и её длина увеличивается, поэтому последний элемент списка
        # оставляется.
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self) -> None:
        """Отрисовывает змейку на экране, затирая след."""
        for position in self.positions:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self) -> tuple[int, int]:
        """
        Метод возвращает текущее положение головы змейки (первый элемент в
        списке positions).
        """
        return self.positions[0]

    def reset(self) -> None:
        """Метод сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        ]


def handle_keys(game_object) -> None:
    """
    Функция обрабатывает нажатия клавиш, чтобы изменить направление движения
    змейки.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


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
    # Тут нужно создать экземпляры классов.
    snake = Snake(body_color=SNAKE_COLOR)
    apple = Apple(body_color=APPLE_COLOR, snake_positions=snake.positions)
    # Общее количество клеток на поле
    total_cells = (SCREEN_WIDTH // GRID_SIZE) * (SCREEN_HEIGHT // GRID_SIZE)

    while True:
        # Очистим экран, заполнив его фоновым цветом (BOARD_BACKGROUND_COLOR).
        screen.fill(BOARD_BACKGROUND_COLOR)

        # Регулируем скорость движения змейки.
        clock.tick(SPEED)

        # Тут опишите основную логику игры.
        # Отрисовка объектов.
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

            # Пересоздаем яблоко с новой случайной позицией.
            apple = Apple(
                body_color=APPLE_COLOR, snake_positions=snake.positions
            )

        # Событие столкновения змейки с собой (если столкновение, сброс игры
        # при помощи метода reset()).
        elif snake.get_head_position() in snake.positions[1:]:
            snake.reset()

        # Теоретическая проверка на заполнение змейкой всего поля)
        if snake.length == total_cells:
            print("Поздравляем! Вы победили!")
            pygame.quit()
            raise SystemExit

        # Обновляем позицию змейки.
        snake.move()

        # Обновление экрана.
        pygame.display.update()


if __name__ == '__main__':
    main()
