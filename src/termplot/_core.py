import shutil
from typing import Iterable
import warnings
import numpy as np

class Figure:
    def __init__(
        self,
        dims: tuple[int, int] = (-1, -1),
        withBorder: bool = True
    ):
        self._withBorder = withBorder
        cols, rows = shutil.get_terminal_size()
        self._dims = (
            dims[0] if dims[0] > 0 else rows - 3, # -3 to leave some vertical buffer
            dims[1] if dims[1] > 0 else cols
        )
        self._lines = self._make_lines(self._dims)
        # TODO: i think i should store the drawableROI instead
        self._drawableDims = self._dims if not self._withBorder else (
            self._dims[0] - 2, self._dims[1] - 2
        )

    def __repr__(self) -> str:
        return f"<termplot.Figure, dims=({self._dims[0]}, {self._dims[1]})>"

    @property
    def lines(self) -> list[list[str]]:
        """
        Primarily for debugging.
        """
        return self._lines

    def __getitem__(self, row: int, col: slice | int) -> list[str]:
        return self._lines[row][col]

    def setLine(self, row: int, line: list[str]):
        if len(line) != self._drawableDims[1]:
            raise ValueError(
                f"Line must be the same length as the drawable width {self._drawableDims[1]}"
            )

        # TODO: handle correctly
        # if row < 0 or row >= self._drawableDims[0]:
        #     raise ValueError(
        #         f"Row must be between 0 and the drawable height {self._drawableDims[0]}"
        #     )

    def _make_lines(self, dims: tuple[int, int]) -> list[list]:
        # pre-allocation for size?
        lines = [[" "] * dims[1] for _ in range(dims[0])]
        return lines

    def stitch(self) -> str:
        return "\n".join(("".join(line) for line in self._lines))

    def _drawBorder(self):
        self._lines[0][0] = "\u256D" # topleft
        self._lines[0][-1] = "\u256E" # topright
        self._lines[-1][0] = "\u2570" # bottomleft
        self._lines[-1][-1] = "\u256F" # bottomright

        # top edge
        self._lines[0][1:-1] = "\u2500" * (self._dims[1] - 2)
        # bottom edge
        self._lines[-1][1:-1] = "\u2500" * (self._dims[1] - 2)
        for i in range(1, self._dims[0]-1):
            # left edge
            self._lines[i][0] = "\u2502"
            # right edge
            self._lines[i][-1] = "\u2502"

    def show(self):
        if self._withBorder:
            self._drawBorder()
        print(f"{self.stitch()}\n")

    def plotBarChart(
        self,
        data: list | tuple | np.ndarray,
        autoExtend: bool = False,
        labels: list[str] | None = None,
        maximumLabelLength: int = 8,
        bounds: tuple[float, float] | None = None,
        symbol: str = "*",
    ):
        if bounds is None:
            bounds = (0, np.max(data))
        span = bounds[1] - bounds[0]

        if labels is None:
            labels = [str(i) for i in range(len(data))]

        chartMaxLength = len(self._lines[0]) - maximumLabelLength
        for i, line in enumerate(self._lines):
            if i >= len(data):
                warnings.warn("More data than lines")
                break
            l = int((data[i] - bounds[0]) / span * chartMaxLength)
            line[:l] = symbol
            line[-maximumLabelLength:] = f"{labels[i]:{maximumLabelLength}}"

        return self._lines

if __name__ == "__main__":
    f = Figure()
    print(f)
    f.plotBarChart([1,2,3])
    f.show()

