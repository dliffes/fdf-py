import os


class FdfError(Exception):
    """Базовый класс для ошибок FdF."""


class MapFormatError(FdfError):
    """Ошибка формата файла карты с указанием строки и колонки."""

    def __init__(self, line: int, column: int, message: str) -> None:
        self.line = line
        self.column = column
        super().__init__(f"строка {line}, колонка {column}: {message}")


def _parse_color(color_str: str, line: int, column: int) -> str:
    """Проверяет шестнадцатеричный цвет 0xRRGGBB (в т.ч. короткий) и возвращает '#RRGGBB'."""
    if not color_str.startswith(("0x", "0X")):
        raise MapFormatError(line, column, f"некорректный формат цвета '{color_str}'")

    hex_part = color_str[2:]
    if not (1 <= len(hex_part) <= 6):
        raise MapFormatError(line, column, f"некорректная длина цвета '{color_str}'")

    try:
        int(hex_part, 16)
    except ValueError as exc:
        raise MapFormatError(line, column, f"некорректный цвет '{color_str}'") from exc

    return f"#{hex_part.zfill(6).upper()}"


def parse_map(file_path: str) -> list[list[tuple[int, str | None]]]:
    """
    Читает файл .fdf и возвращает двумерный массив точек.
    Каждая точка представлена как кортеж: (высота_z, цвет_строкой_или_None).
    """
    if not os.path.exists(file_path):
        raise OSError(f"Файл не найден: {file_path}")

    matrix: list[list[tuple[int, str | None]]] = []

    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()

    while lines and lines[-1].strip() == "":
        lines.pop()

    if not lines:
        raise MapFormatError(1, 1, "файл пуст")

    row_length: int | None = None

    for y, line_content in enumerate(lines, start=1):
        tokens = line_content.strip().split()
        if not tokens:
            raise MapFormatError(y, 1, "пустая строка в середине файла")

        if row_length is None:
            row_length = len(tokens)
        elif len(tokens) != row_length:
            raise MapFormatError(y, len(tokens) + 1, "строка имеет неверную длину")

        row: list[tuple[int, str | None]] = []
        for x, token in enumerate(tokens, start=1):
            color: str | None = None
            if "," in token:
                parts = token.split(",")
                if len(parts) != 2:
                    raise MapFormatError(y, x, f"некорректный формат значения '{token}'")
                val_str, color_str = parts
                color = _parse_color(color_str, y, x)
            else:
                val_str = token

            try:
                z = int(val_str)
            except ValueError as exc:
                raise MapFormatError(y, x, f"'{val_str}' — не целое число") from exc

            row.append((z, color))
        matrix.append(row)

    if not matrix:
        raise MapFormatError(1, 1, "файл не содержит корректных данных")

    return matrix