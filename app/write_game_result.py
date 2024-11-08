import os
from datetime import datetime


CURRENT_DIR: str = os.path.dirname(__file__)


def write_game_result(
        snake_lenght: int,
        user_nickname: str = 'USER',
        file_name: str = 'game_results.csv'
) -> None:
    """Запись результатов игры в .csv файл."""
    file_dir = os.path.join(CURRENT_DIR, '..')
    file_path = os.path.join(file_dir, file_name)
    current_datetime = datetime.now().strftime('%d.%m.%Y (%H:%M:%S)')
    result = f'{current_datetime}\t{user_nickname}\t{snake_lenght}'
    with open(file_path, 'a', encoding='UTF-8') as f:
        f.write(result + '\n')


if __name__ == '__main__':
    write_game_result(5)
    write_game_result(8)
    write_game_result(1)
