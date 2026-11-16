import math

from fdf.model import Map, Point


class Camera:
    """Менеджер для управления масштабом, смещением и проекцией точек."""
    def __init__(self, width: int, height: int) -> None:
        self.width = width        # Ширина графического окна
        self.height = height      # Высота графического окна
        self.scale: float = 1.0   # Масштаб увеличения
        self.offset_x: float = 0.0 # Смещение по X
        self.offset_y: float = 0.0 # Смещение по Y
        self.z_scale: float = 1.0  # Коэффициент высоты гор
        self.is_iso: bool = True   # Включена ли изометрия (для доп. заданий)

    def fit(self, map_obj: Map) -> None:
        """Автоматически подбирает масштаб и центрирует карту в окне."""
        if map_obj.width == 0 or map_obj.height == 0:
            return

        # 1. Пробный прогон при scale = 1 и нулевых смещениях для поиска мин/макс
        min_x, max_x = float('inf'), float('-inf')
        min_y, max_y = float('inf'), float('-inf')

        # Уголок для расчетов угла 30 градусов
        cos30 = math.cos(math.radians(30))
        sin30 = math.sin(math.radians(30))

        for row in map_obj:
            for p in row:
                if self.is_iso:
                    px = (p.x - p.y) * cos30
                    py = (p.x + p.y) * sin30 - p.z * self.z_scale
                else:
                    px = p.x
                    py = p.y
                
                min_x = min(min_x, px)
                max_x = max(max_x, px)
                min_y = min(min_y, py)
                max_y = max(max_y, py)

        map_width = max_x - min_x
        map_height = max_y - min_y

        if map_width == 0:
            map_width = 1
        if map_height == 0:
            map_height = 1

        # 2. Вычисляем масштаб с запасом 90% от размера окна
        scale_x = self.width / map_width
        scale_y = self.height / map_height
        self.scale = min(scale_x, scale_y) * 0.9

        # 3. Центрируем карту в окне
        proj_center_x = (min_x + max_x) / 2 * self.scale
        proj_center_y = (min_y + max_y) / 2 * self.scale

        self.offset_x = self.width / 2 - proj_center_x
        self.offset_y = self.height / 2 - proj_center_y

    def project_point(self, p: Point) -> tuple[float, float]:
        """Превращает одну 3D-точку (x, y, z) в 2D-координаты экрана (X, Y)."""
        cos30 = math.cos(math.radians(30))
        sin30 = math.sin(math.radians(30))

        if self.is_iso:
            # Классические формулы изометрии из задания
            x_prime = (p.x - p.y) * cos30
            y_prime = (p.x + p.y) * sin30 - p.z * self.z_scale
        else:
            # Вид сверху (для дополнительного задания)
            x_prime = p.x
            y_prime = p.y

        # Масштабирование и смещение к центру экрана
        screen_x = x_prime * self.scale + self.offset_x
        screen_y = y_prime * self.scale + self.offset_y

        return screen_x, screen_y