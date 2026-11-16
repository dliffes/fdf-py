import sys
import traceback
from fdf.parser import parse_map, FdfError
from fdf.model import Map
from fdf.app import App


def main() -> None:
    print("=== Старт программы ===")
    if len(sys.argv) != 2:
        print("Использование: python main.py <файл.fdf>", file=sys.stderr)
        sys.exit(2)

    file_path = sys.argv[1]
    print(f"Открываем файл: {file_path}")

    try:
        raw_data = parse_map(file_path)
        print("Файл успешно распарсен, создаем модель карты...")
        map_obj = Map(raw_data)
        print("Карта создана. Запускаем графическое окно App...")
        
        app = App(map_obj)
        print("Окно инициализировано, входим в mainloop()...")
        app.mainloop()
        print("Работа программы завершена штатно.")
    except Exception as e:
        print("\n[!] ПРОИЗОШЛА ОШИБКА:", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()