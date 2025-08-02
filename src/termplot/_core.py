import shutil

class Figure:
    def __init__(
        self,
        dims: tuple[int, int] = (-1, -1)
    ):
        rows, cols = shutil.get_terminal_size()
        self._dims = (
            dims[0] if dims[0] > 0 else rows,
            dims[1] if dims[1] > 0 else cols
        )
        self._lines = self._make_lines(self._dims)

    def __repr__(self) -> str:
        return f"<termplot.Figure, dims=({self._dims[0]}, {self._dims[1]})>"

    def _make_lines(self, dims: tuple[int, int]) -> list[str]:
        lines = [" " * dims[1] for _ in range(dims[0])]
        return lines

    def stitch(self) -> str:
        return "\n".join(self._lines)

    def show(self):
        print(f"{self.stitch()}\n")

