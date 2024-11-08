import os


CURRENT_DIR: str = os.path.dirname(__file__)


def read_game_record(file_name: str = 'game_results.csv') -> int:
    """Чтение рекордной длины змейки."""
    file_dir = os.path.join(CURRENT_DIR, '..')
    file_path = os.path.join(file_dir, file_name)
    if os.path.exists(file_path):
        records = [0]
        with open(file_path, mode='r', encoding='utf-8') as file:
            for line in file:
                records.append(int(line.split('\t')[-1]))
        return max(records)
    return 0


if __name__ == '__main__':
    record = read_game_record()
    print(record)
