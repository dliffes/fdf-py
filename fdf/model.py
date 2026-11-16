from collections.abc import Iterator


class Point:
    """Класс, описывающий отдельную точку на карте с координатами (x, y, z) и цветом."""
    def __init__(self, x: int, y: int, z: int, color: str | None = None) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.color = color  # Цвет в формате "#RRGGBB" или None

    def __repr__(self) -> str:
        return f"Point(x={self.x}, y={self.y}, z={self.z}, color={self.color})"


class Map:
    """Класс, описывающий всю карту высот целиком."""
    def __init__(self, raw_data: list[list[tuple[int, str | None]]]) -> None:
        """Принимает двумерный массив из парсера и преобразует его в сетку объектов Point."""
        self.height: int = len(raw_data)
        self.width: int = len(raw_data[0]) if self.height > 0 else 0
        
        # Создаем двумерный список объектов Point
        self.points: list[list[Point]] = []
        for y, row in enumerate(raw_data):
            point_row: list[Point] = []
            for x, (z, color) in enumerate(row):
                point_row.append(Point(x, y, z, color))
            self.points.append(point_row)

    def __len__(self) -> int:
        """Возвращает количество строк в карте."""
        return self.height

    def __iter__(self) -> Iterator[list[Point]]:
        """Позволяет перебирать ряды карты в цикле for."""
        return iter(self.points)

    def neighbors(self, x: int, y: int) -> list[Point]:
        """
        Возвращает список соседей для точки (x, y).
        Согласно условию FdF, рёбра строятся к соседу справа и к соседу снизу.
        """
        result: list[Point] = []
        # Сосед справа (x + 1, y)
        if x + 1 < self.width:
            result.append(self.points[y][x + 1])
        # Сосед снизу (x, y + 1)
        if y + 1 < self.height:
            result.append(self.points[y + 1][x])
        return result