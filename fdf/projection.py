import math

from fdf.model import Map, Point


class Camera:
    """Менеджер для управления масштабом, смещением и проекцией точек."""

    def __init__(self, width: int, height: int) -> None:
        self.width = width          # Ширина графического окна
        self.height = height        # Высота графического окна
        self.scale: float = 1.0     # Масштаб увеличения
        self.offset_x: float = 0.0  # Смещение по X
        self.offset_y: float = 0.0  # Смещение по Y
        self.z_scale: float = 1.0   # Коэффициент высоты гор
        self.is_iso: bool = True    # Включена ли изометрия (для доп. заданий)
        self.angle: float = 0.0     # Угол поворота в градусах
        self._pivot_x: float = 0.0  # Центр карты по X для поворота
        self._pivot_y: float = 0.0  # Центр карты по Y для поворота

    def _rotate_xy(self, x: float, y: float) -> tuple[float, float]:
        """Поворачивает координаты (x, y) вокруг центра карты на self.angle."""
        dx = x - self._pivot_x
        dy = y - self._pivot_y
        if self.angle == 0.0:
            return dx, dy

        rad = math.radians(self.angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        rx = dx * cos_a - dy * sin_a
        ry = dx * sin_a + dy * cos_a
        return rx, ry

    def _project_raw(self, p: Point) -> tuple[float, float]:
        """Проецирует точку с учётом поворота и режима (изометрия / вид сверху)."""
        rx, ry = self._rotate_xy(float(p.x), float(p.y))

        if self.is_iso:
            cos30 = math.cos(math.radians(30))
            sin30 = math.sin(math.radians(30))
            x_prime = (rx - ry) * cos30
            y_prime = (rx + ry) * sin30 - p.z * self.z_scale
        else:
            x_prime = rx
            y_prime = ry

        return x_prime, y_prime

    def fit(self, map_obj: Map) -> None:
        """Автоматически подбирает масштаб и центрирует карту в окне."""
        if map_obj.width == 0 or map_obj.height == 0:
            return

        self._pivot_x = (map_obj.width - 1) / 2.0
        self._pivot_y = (map_obj.height - 1) / 2.0

        min_x, max_x = float("inf"), float("-inf")
        min_y, max_y = float("inf"), float("-inf")

        for row in map_obj:
            for p in row:
                px, py = self._project_raw(p)
                min_x = min(min_x, px)
                max_x = max(max_x, px)
                min_y = min(min_y, py)
                max_y = max(max_y, py)

        map_width = max_x - min_x
        map_height = max_y - min_y

        if map_width == 0:
            map_width = 1.0
        if map_height == 0:
            map_height = 1.0

        scale_x = self.width / map_width
        scale_y = self.height / map_height
        self.scale = min(scale_x, scale_y) * 0.9

        proj_center_x = (min_x + max_x) / 2 * self.scale
        proj_center_y = (min_y + max_y) / 2 * self.scale

        self.offset_x = self.width / 2 - proj_center_x
        self.offset_y = self.height / 2 - proj_center_y

    def pan(self, dx: float, dy: float) -> None:
        """Сдвигает проекцию карты по осям экрана."""
        self.offset_x += dx
        self.offset_y += dy

    def zoom(
        self,
        factor: float,
        anchor_x: float | None = None,
        anchor_y: float | None = None,
        min_scale: float = 0.05,
        max_scale: float = 200.0,
    ) -> None:
        """Масштабирует карту без смещения опорной точки (по умолчанию центра окна)."""
        if factor <= 0 or self.scale <= 0:
            return

        cx = self.width / 2.0 if anchor_x is None else anchor_x
        cy = self.height / 2.0 if anchor_y is None else anchor_y

        new_scale = max(min_scale, min(max_scale, self.scale * factor))
        if new_scale == self.scale:
            return

        world_x = (cx - self.offset_x) / self.scale
        world_y = (cy - self.offset_y) / self.scale

        self.scale = new_scale
        self.offset_x = cx - world_x * self.scale
        self.offset_y = cy - world_y * self.scale

    def adjust_z_scale(
        self,
        delta: float,
        min_z: float = 0.05,
        max_z: float = 20.0,
    ) -> None:
        """Изменяет коэффициент масштабирования высоты z_scale."""
        self.z_scale = max(min_z, min(max_z, self.z_scale + delta))

    def toggle_top_view(self, map_obj: Map | None = None) -> None:
        """Переключает режим проекции: изометрия или вид сверху (X = x, Y = y)."""
        self.is_iso = not self.is_iso
        if map_obj is not None:
            self.fit(map_obj)

    def rotate(self, delta_deg: float) -> None:
        """Изменяет угол поворота карты в градусах."""
        self.angle = (self.angle + delta_deg) % 360.0

    def project_point(self, p: Point) -> tuple[float, float]:
        """Превращает одну 3D-точку (x, y, z) в 2D-координаты экрана (X, Y)."""
        x_prime, y_prime = self._project_raw(p)
        screen_x = x_prime * self.scale + self.offset_x
        screen_y = y_prime * self.scale + self.offset_y
        return screen_x, screen_y