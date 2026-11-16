import os
from typing import List, Tuple, Optional

class FdfError(Exception):
    """Базовый класс для ошибок FdF."""
    pass

class MapFormatError(FdfError):
    """Ошибка формата файла карты с указанием строки и колонки."""
    def __init__(self, line: int, column: int, message: str) -> None:
        self.line = line
        self.column = column
        super().__init__(f"строка {line}, колонка {column}: {message}")


def parse_map(file_path: str) -> List[List[Tuple[int, Optional[str]]]]:
    """
    Читает файл .fdf и возвращает двумерный массив точек.
    Каждая точка представлена как кортеж: (высота_z, цвет_строкой_или_None).
    """
    if not os.path.exists(file_path):
        raise OSError(f"Файл не найден: {file_path}")

    matrix: List[List[Tuple[int, Optional[str]]]] = []

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Фильтруем пустые строки в конце файла
    while lines and lines[-1].strip() == '':
        lines.pop()

    if not lines:
        raise MapFormatError(1, 1, "файл пуст")

    row_length = None

    for y, line_content in enumerate(lines, start=1):
        tokens = line_content.strip().split()
        if not tokens:
            continue

        if row_length is None:
            row_length = len(tokens)
        elif len(tokens) != row_length:
            raise MapFormatError(y, len(tokens) + 1, "строка имеет неверную длину")

        row: List[Tuple[int, Optional[str]]] = []
        for x, token in enumerate(tokens, start=1):
            color = None
            if ',' in token:
                parts = token.split(',')
                if len(parts) != 2:
                    raise MapFormatError(y, x, f"некорректный формат значения '{token}'")
                val_str, color_str = parts
                if not (color_str.startswith('0x') or color_str.startswith('0X')):
                    raise MapFormatError(y, x, f"некорректный формат цвета '{color_str}'")
                color = color_str.upper()
            else:
                val_str = token

            try:
                z = int(val_str)
            except ValueError:
                raise MapFormatError(y, x, f"'{val_str}' — не целое число")

            row.append((z, color))
        matrix.append(row)

    if not matrix:
        raise MapFormatError(1, 1, "файл не содержит корректных данных")

    return matrix