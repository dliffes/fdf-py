import tkinter as tk

from fdf.model import Map
from fdf.projection import Camera


class App(tk.Tk):
    """Главное графическое окно приложения FdF на Tkinter."""

    PAN_STEP = 25.0
    ZOOM_IN_FACTOR = 1.15
    ZOOM_OUT_FACTOR = 1.0 / 1.15
    Z_SCALE_STEP = 0.2
    ROTATE_STEP = 5.0

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
        self.bind("<KP_Add>", lambda event: self._change_z_scale(self.Z_SCALE_STEP))
        self.bind("-", lambda event: self._change_z_scale(-self.Z_SCALE_STEP))
        self.bind("<KP_Subtract>", lambda event: self._change_z_scale(-self.Z_SCALE_STEP))

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

    def draw(self) -> None:
        """Очищает холст и рисует каркас карты (линии между соседями)."""
        self.canvas.delete("all")

        for y, row in enumerate(self.map_obj):
            for x, p in enumerate(row):
                x1, y1 = self.camera.project_point(p)

                for neighbor in self.map_obj.neighbors(x, y):
                    x2, y2 = self.camera.project_point(neighbor)

                    line_color = p.color if p.color else "#4A90E2"
                    self.canvas.create_line(x1, y1, x2, y2, fill=line_color, width=1)