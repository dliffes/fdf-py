import pytest

from fdf.model import Map
from fdf.parser import parse_map
from fdf.projection import height_color, lerp_color


def test_lerp_color_endpoints_and_midpoint() -> None:
    assert lerp_color("#FF0000", "#0000FF", 0.0) == "#FF0000"
    assert lerp_color("#FF0000", "#0000FF", 1.0) == "#0000FF"
    assert lerp_color("#FF0000", "#0000FF", 0.5) == "#800080"


def test_lerp_color_clamps_t() -> None:
    assert lerp_color("#102030", "#405060", -0.5) == "#102030"
    assert lerp_color("#102030", "#405060", 1.5) == "#405060"


def test_height_color_range_and_flat_map() -> None:
    assert height_color(0, 0, 10) == "#3B82F6"
    assert height_color(10, 0, 10) == "#EF4444"
    mid = height_color(5, 0, 10)
    assert mid.startswith("#") and len(mid) == 7
    assert height_color(3, 3, 3) == "#3B82F6"


@pytest.mark.parametrize(
    ("raw_line", "expected_color"),
    [
        ("1,0xff", "#0000FF"),
        ("2,0xFF00", "#00FF00"),
        ("5,0xFF0000", "#FF0000"),
        ("0", None),
    ],
)
def test_parse_short_and_full_hex_colors(
    tmp_path: pytest.TempPathFactory,
    raw_line: str,
    expected_color: str | None,
) -> None:
    fdf_file = tmp_path / "sample.fdf"  # type: ignore[operator]
    fdf_file.write_text(f"{raw_line}\n", encoding="utf-8")
    m = Map(parse_map(str(fdf_file)))
    assert m.points[0][0].color == expected_color