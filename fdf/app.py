import tkinter as tk
from typing import Optional
from fdf.model import Map
from fdf.projection import Camera


class App(tk.Tk):
    """Главное графическое окно приложения FdF на Tkinter."""
    def __init__(self, map_obj: Map) -> None:
        super().__init__()
        self.title("FdF — каркасная 3D-модель карты высот")
        self.geometry("1024x768")
        
        self.map_obj = map_obj
        
        # Создаем холст для рисования линий
        self.canvas = tk.Canvas(self, bg="#111111", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Инициализируем камеру под размеры окна
        self.camera = Camera(1024, 768)
        self.camera.fit(self.map_obj)
        
        # Привязываем события
        self.bind("<Escape>", lambda event: self.destroy())
        self.bind("<Configure>", self.on_resize)
        
        # Первая отрисовка карты
        self.draw()

    def on_resize(self, event: tk.Event) -> None:
        """Пересчитывает проекцию и перерисовывает карту при изменении размера окна."""
        self.camera.width = event.width
        self.camera.height = event.height
        self.camera.fit(self.map_obj)
        self.draw()

    def draw(self) -> None:
        """Очищает холст и рисует каркас карты (линии между соседями)."""
        self.canvas.delete("all")
        
        # Проходим по всем точкам карты
        for y, row in enumerate(self.map_obj):
            for x, p in enumerate(row):
                # Проецируем текущую 3D точку в 2D координаты экрана
                x1, y1 = self.camera.project_point(p)
                
                # Получаем соседей (справа и снизу) для построения ребер
                for neighbor in self.map_obj.neighbors(x, y):
                    x2, y2 = self.camera.project_point(neighbor)
                    
                    # Цвет ребра: если у точки задан цвет, используем его, иначе синеватый
                    line_color = p.color if p.color else "#4A90E2"
                    
                    # Рисуем линию на холсте
                    self.canvas.create_line(x1, y1, x2, y2, fill=line_color, width=1)