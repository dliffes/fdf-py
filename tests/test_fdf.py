from pathlib import Path

import pytest

from fdf.model import Map, Point
from fdf.parser import MapFormatError, parse_map
from fdf.projection import Camera


def test_parse_elem_map(tmp_path: Path) -> None:
    map_file = tmp_path / "elem.fdf"
    map_file.write_text(
        "0 0 0 0 0\n"
        "0 2 2 2 0\n"
        "0 2 5 2 0\n"
        "0 2 2 2 0\n"
        "0 0 0 0 0\n",
        encoding="utf-8",
    )
    raw = parse_map(str(map_file))
    m = Map(raw)

    assert len(m) == 5
    assert m.width == 5
    assert m.height == 5
    assert m.points[2][2].z == 5
    assert m.points[2][2].x == 2
    assert m.points[2][2].y == 2


@pytest.mark.parametrize(
    ("token", "expected_z", "expected_color"),
    [
        ("7", 7, None),
        ("-3", -3, None),
        ("2,0xFF8800", 2, "#FF8800"),
        ("1,0xff", 1, "#0000FF"),
    ],
)
def test_parse_cell_values(
    tmp_path: Path, token: str, expected_z: int, expected_color: str | None
) -> None:
    map_file = tmp_path / "cell.fdf"
    map_file.write_text(f"{token}\n", encoding="utf-8")

    raw = parse_map(str(map_file))
    assert raw == [[(expected_z, expected_color)]]


@pytest.mark.parametrize(
    "bad_content",
    [
        "",
        "0 2 x 2 0\n0 2 5 2 0\n",
        "0 0 0\n0 0\n",
        "1,not_a_color\n",
        "1,0xZZZZZZ\n",
        "1,0x1234567\n",
    ],
)
def test_parse_bad_maps_raises(tmp_path: Path, bad_content: str) -> None:
    bad_file = tmp_path / "bad.fdf"
    bad_file.write_text(bad_content, encoding="utf-8")

    with pytest.raises(MapFormatError):
        parse_map(str(bad_file))


def test_parse_missing_file_raises_oserror() -> None:
    with pytest.raises(OSError):
        parse_map("non_existent_map_file.fdf")


def test_model_iteration_and_neighbors() -> None:
    raw = [
        [(0, None), (1, None)],
        [(2, None), (3, None)],
    ]
    m = Map(raw)

    assert len(m) == 2
    rows = list(m)
    assert len(rows) == 2

    top_left_neighbors = m.neighbors(0, 0)
    assert [(p.x, p.y) for p in top_left_neighbors] == [(1, 0), (0, 1)]

    bottom_right_neighbors = m.neighbors(1, 1)
    assert bottom_right_neighbors == []


def test_camera_projection_origin_and_height() -> None:
    cam = Camera(800, 600)
    x0, y0 = cam.project_point(Point(0, 0, 0))
    assert x0 == pytest.approx(0.0)
    assert y0 == pytest.approx(0.0)

    _, y_up = cam.project_point(Point(0, 0, 1))
    assert y_up < 0


def test_camera_fit_keeps_points_inside_window() -> None:
    raw = [
        [(0, None), (2, None), (0, None)],
        [(2, None), (5, None), (2, None)],
        [(0, None), (2, None), (0, None)],
    ]
    m = Map(raw)
    cam = Camera(800, 600)
    cam.fit(m)

    for row in m:
        for pt in row:
            sx, sy = cam.project_point(pt)
            assert 0 <= sx <= 800
            assert 0 <= sy <= 600