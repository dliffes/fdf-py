import sys

from fdf.app import App
from fdf.model import Map
from fdf.parser import FdfError, parse_map


def main() -> None:
    if len(sys.argv) != 2:
        print("Использование: python main.py <файл.fdf>", file=sys.stderr)
        sys.exit(2)

    file_path = sys.argv[1]

    try:
        raw_data = parse_map(file_path)
        map_obj = Map(raw_data)
        app = App(map_obj)
        app.mainloop()
    except (FdfError, OSError) as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()