import tkinter as tk

from fdf.model import Map, Point
from fdf.projection import Camera, height_color, lerp_color


class App(tk.Tk):
    """Главное графическое окно приложения FdF на Tkinter."""

    PAN_STEP = 25.0
    ZOOM_IN_FACTOR = 1.15
    ZOOM_OUT_FACTOR = 1.0 / 1.15
    Z_SCALE_STEP = 0.2
    ROTATE_STEP = 5.0
    EDGE_SEGMENTS = 12

    def __init__(self, map_obj: Map) -> None:
        super().__init__()
        self.title("FdF — каркасная 3D-модель карты высот")
        self.geometry("1024x768")

        self.map_obj = map_obj

        self.canvas = tk.Canvas(self, bg="#111111", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.camera = Camera(1024, 768)
        self.camera.fit(self.map_obj)

        # Базовые и навигационные события
        self.bind("<Escape>", lambda event: self.destroy())
        self.bind("<Configure>", self.on_resize)

        # Сдвиг стрелками
        self.bind("<Left>", lambda event: self._pan(self.PAN_STEP, 0.0))
        self.bind("<Right>", lambda event: self._pan(-self.PAN_STEP, 0.0))
        self.bind("<Up>", lambda event: self._pan(0.0, self.PAN_STEP))
        self.bind("<Down>", lambda event: self._pan(0.0, -self.PAN_STEP))

        # Масштабирование колёсиком мыши (центрируем по центру окна, чтобы картинка не смещалась)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Button-4>", lambda event: self._zoom(self.ZOOM_IN_FACTOR))
        self.canvas.bind("<Button-5>", lambda event: self._zoom(self.ZOOM_OUT_FACTOR))

        # Изменение высоты (+ / -)
        self.bind("+", lambda event: self._change_z_scale(self.Z_SCALE_STEP))
        self.bind("=", lambda event: self._change_z_scale(self.Z_SCALE_STEP))
        self.bind("-", lambda event: self._change_z_scale(-self.Z_SCALE_STEP))
   
        # Поворот карты (q / e)
        self.bind("q", lambda event: self._rotate(-self.ROTATE_STEP))
        self.bind("e", lambda event: self._rotate(self.ROTATE_STEP))

        # Переключение вида сверху (изометрия / top view)
        self.bind("t", lambda event: self._toggle_top_view())
        self.bind("T", lambda event: self._toggle_top_view())

        self.draw()

    def _toggle_top_view(self) -> None:
        self.camera.toggle_top_view(self.map_obj)
        self.draw()

    def _rotate(self, delta_deg: float) -> None:
        self.camera.rotate(delta_deg)
        self.draw()

    def _change_z_scale(self, delta: float) -> None:
        """Изменяет масштаб высоты (z_scale) и перерисовывает модель."""
        self.camera.adjust_z_scale(delta)
        self.draw()  
        
    def _pan(self, dx: float, dy: float) -> None:
        self.camera.pan(dx, dy)
        self.draw()

    def _zoom(self, factor: float) -> None:
        self.camera.zoom(factor)
        self.draw()

    def on_mouse_wheel(self, event: tk.Event) -> None:
        """Обрабатывает прокрутку колёсика мыши без смещения центра изображения."""
        if event.delta > 0:
            self._zoom(self.ZOOM_IN_FACTOR)
        elif event.delta < 0:
            self._zoom(self.ZOOM_OUT_FACTOR)

    def on_resize(self, event: tk.Event) -> None:
        """Пересчитывает проекцию и перерисовывает карту при изменении размера окна."""
        if event.width <= 1 or event.height <= 1:
            return
        self.camera.width = event.width
        self.camera.height = event.height
        self.camera.fit(self.map_obj)
        self.draw()

    def _point_color(self, p: Point, z_min: int, z_max: int) -> str:
        if p.color is not None:
            return p.color
        return height_color(p.z, z_min, z_max)

    def _draw_edge(
        self,
        x1: float,
        y1: float,
        color1: str,
        x2: float,
        y2: float,
        color2: str,
    ) -> None:
        if color1 == color2:
            self.canvas.create_line(x1, y1, x2, y2, fill=color1, width=1)
            return

        n = self.EDGE_SEGMENTS
        for i in range(n):
            t0 = i / n
            t1 = (i + 1) / n
            sx1 = x1 + (x2 - x1) * t0
            sy1 = y1 + (y2 - y1) * t0
            sx2 = x1 + (x2 - x1) * t1
            sy2 = y1 + (y2 - y1) * t1
            seg_color = lerp_color(color1, color2, (i + 0.5) / n)
            self.canvas.create_line(sx1, sy1, sx2, sy2, fill=seg_color, width=1)

    def draw(self) -> None:
        """Очищает холст и рисует каркас карты (линии между соседями)."""
        self.canvas.delete("all")

        all_z = [p.z for row in self.map_obj for p in row]
        if not all_z:
            return
        z_min, z_max = min(all_z), max(all_z)

        for y, row in enumerate(self.map_obj):
            for x, p in enumerate(row):
                x1, y1 = self.camera.project_point(p)
                c1 = self._point_color(p, z_min, z_max)

                for neighbor in self.map_obj.neighbors(x, y):
                    x2, y2 = self.camera.project_point(neighbor)
                    c2 = self._point_color(neighbor, z_min, z_max)
                    self._draw_edge(x1, y1, c1, x2, y2, c2)