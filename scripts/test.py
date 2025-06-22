test = '''import pytest

@pytest.mark.parametrize("side, expected", [
    (10, 40),
    (20, 80),
    (-5, None),
    (0, None)
])
def test_rect_area(side, expected):
    if side < 0:
        with pytest.raises(ValueError):
            my_pkg.rect_area(side)
    else:
        assert my_pkg.rect_area(side) == expected

@pytest.mark.parametrize("side, expected", [
    (10, 40),
    (20, 80),
    (-5, None),
    (0, None)
])
def test_square_perimeter(side, expected):
    if side < 0:
        with pytest.raises(ValueError):
            my_pkg.perimeter.square_perimeter(side)
    else:
        assert my_pkg.perimeter.square_perimeter(side) == expected

def test_invalid_input():
    with pytest.raises(TypeError):
        my_pkg.rect_area("a")

def test_invalid_input2():
    with pytest.raises(TypeError):
        my_pkg.perimeter.square_perimeter("a")
'''

test1 = '''```     
import pytest
from module import rect_area, square_area

def test_rect_area():
    assert rect_area(1, 2) == 2
    assert rect_area(-1, -2) == -2
    assert rect_area(0, 1) == 0

def test_square_area():
    assert square_area(1) == 1
    assert square_area(-1) == -1
    assert square_area(0) == 0

def test_error_handling():
    with pytest.raises(ValueError):
        rect_area("a", "b")
    with pytest.raises(TypeError):
        rect_area(1, "b")
    with pytest.raises(TypeError):
        square_area("a")
```'''
test2 = """```
import pytest
from my_pkg import rect_area, square_perimeter

def test_rect_area():
    assert rect_area(5, 6) == 30

def test_square_perimeter():
    assert square_perimeter(4) == 16

def test_invalid_input():
    with pytest.raises(ValueError):
        rect_area(-1, -2)
```
This is a complete pytest-style unit test file for the provided Python module `my_pkg`. The file imports the necessary functions from the module and includes test functions that cover normal behavior, edge cases, error handling, and other important aspects of testing. Each test function starts with `test_` to indicate its purpose and is defined within a separate scope to allow for independent execution.

The first two tests, `test_rect_area()` and `test_square_perimeter()`, ensure that the module's functions work correctly for valid input values. The first test checks the area of a 5x6 rectangle, which should have an area of 30. The second test checks the perimeter of a square with side length 4, which should have a perimeter of 16.

The third test, `test_invalid_input()`, verifies that the module's functions raise an error when invalid input values are provided. This is important to ensure that the code handles unexpected or malicious input gracefully and doesn't produce incorrect results or crash. In this case, the function raises a `ValueError` exception when negative values are passed as arguments, indicating that the input is invalid.

Overall, this test file provides comprehensive coverage of the provided Python module `my_pkg`, ensuring that it works correctly for various input values and handles errors appropriately.

"""

def strip_markdown_fences(code: str) -> str:
    """Remove markdown fences and leading/explanatory lines."""
    # lines = code.splitlines()
    clean_lines = []
    for block in code.split("```"):
        # print(f"\n\nProcessing block: {block}")
        if block and not block.startswith("```") and "import p" in block:
            # print(f"\n\nAdding block: {block}")
            clean_lines.append(block)

    return "\n".join(clean_lines)

print("[FINAL]\n\n\n", strip_markdown_fences(test2))
