import shutil
from typing import Iterable, Tuple
import warnings
import numpy as np

class Figure:
    def __init__(
        self,
        dims: tuple[int, int] = (-1, -1)
    ):
        cols, rows = shutil.get_terminal_size()
        self._dims = (
            dims[0] if dims[0] > 0 else rows - 3, # -3 to leave some vertical buffer
            dims[1] if dims[1] > 0 else cols
        )
        self._lines = self._make_lines(self._dims)
        self._drawableDims = (
            self._dims[0] - 2, self._dims[1] - 2
        )

    def __repr__(self) -> str:
        return f"<termplot.Figure, dims=({self._dims[0]}, {self._dims[1]})>"

    @property
    def lines(self) -> list[list[str]]:
        """
        Primarily for debugging. Includes the border characters.
        """
        return self._lines

    # ============================ INDEXING ============================

    def _translate_border_row_index(self, idx: int):
        return self._dims[0] - 1 + idx if idx < 0 else idx + 1

    def _translate_border_col_index(self, idx: int):
        return self._dims[1] - 1 + idx if idx < 0 else idx + 1

    def _index_without_border(
        self,
        row: slice | int,
        col: slice | int
    ) -> tuple[slice | int, slice | int]:
        if isinstance(row, slice):
            if row.start is None:
                rowstart = self._translate_border_row_index(0)
            else:
                rowstart = self._translate_border_row_index(row.start)

            if row.stop is None:
                rowstop = self._translate_border_row_index(self._drawableDims[0])
            else:
                rowstop = self._translate_border_row_index(row.stop)

            row = slice(rowstart, rowstop)
        else:
            row = self._translate_border_row_index(row)

        if isinstance(col, slice):
            if col.start is None:
                colstart = self._translate_border_col_index(0)
            else:
                colstart = self._translate_border_col_index(col.start)

            if col.stop is None:
                colstop = self._translate_border_col_index(self._drawableDims[1])
            else:
                colstop = self._translate_border_col_index(col.stop)

            col = slice(colstart, colstop)
        else:
            col = self._translate_border_col_index(col)

        return row, col

    def __getitem__(
        self,
        index: Tuple[slice | int, slice | int]
    ) -> list[list[str]]:
        row, col = self._index_without_border(index[0], index[1])
        return self._lines[row][col]

    def __setitem__(
        self,
        index: Tuple[slice | int, slice | int],
        value: str | list[str]
    ):
        row, col = self._index_without_border(index[0], index[1])
        if isinstance(row, int):
            prevLineLength = len(self._lines[row])
            self._lines[row][col] = value
            if len(self._lines[row]) != prevLineLength:
                raise ValueError("Setting line caused change in length")
        else:
            for i, line in enumerate(self._lines):
                prevLineLength = len(line)
                line[col] = value[i]
                if len(line) != prevLineLength:
                    raise ValueError("Setting line caused change in length")

    # ========================== DRAWING ==============================

    def _make_lines(self, dims: tuple[int, int]) -> list[list]:
        # pre-allocation for size?
        lines = [[" "] * dims[1] for _ in range(dims[0])]
        return lines

    def stitch(self, lastOccupiedRow: int | None = None) -> str:
        lastOccupiedRow = self._dims[1] - 2 if lastOccupiedRow is None else lastOccupiedRow
        return "\n".join(("".join(line) for i, line in enumerate(self._lines) if i <= lastOccupiedRow + 1))

    def _getLastOccupiedRow(self):
        occupiedRows = [
            i for i, line in enumerate(self._lines)
            if not all([j == " " for j in line])
        ]
        lastRow = np.max(occupiedRows)
        return lastRow

    def _drawBorder(self, lastOccupiedRow: int | None = None):
        # With border, default is -2 for last occupied row, since -1 is the border itself
        lastOccupiedRow = self._dims[0] - 2 if lastOccupiedRow is None else lastOccupiedRow
        self._lines[0][0] = "\u256D" # topleft
        self._lines[0][-1] = "\u256E" # topright
        self._lines[lastOccupiedRow+1][0] = "\u2570" # bottomleft
        self._lines[lastOccupiedRow+1][-1] = "\u256F" # bottomright

        # top edge
        self._lines[0][1:-1] = "\u2500" * (self._dims[1] - 2)
        # bottom edge
        self._lines[lastOccupiedRow+1][1:-1] = "\u2500" * (self._dims[1] - 2)
        for i in range(1, lastOccupiedRow + 1):
            # left edge
            self._lines[i][0] = "\u2502"
            # right edge
            self._lines[i][-1] = "\u2502"

    def show(self, shrinkToFit: bool = True) -> str:
        lastOccupiedRow = self._getLastOccupiedRow() if shrinkToFit else None
        self._drawBorder(lastOccupiedRow)
        toPrint = self.stitch(lastOccupiedRow)
        print(f"{toPrint}\n")
        return toPrint

    def plotBarChart(
        self,
        data: list | tuple | np.ndarray,
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

        chartMaxLength = self._drawableDims[1] - maximumLabelLength
        if len(data) > self._drawableDims[0]:
            raise ValueError(f"More data ({len(data)}) than lines ({self._drawableDims[0]})")
        for i in range(len(data)):
            l = int((data[i] - bounds[0]) / span * chartMaxLength)
            self[i, :l] = [symbol] * l

            labelstr = f" {labels[i]:{maximumLabelLength-1}}"
            self[i, -maximumLabelLength:] = labelstr

        return self._lines

if __name__ == "__main__":
    f = Figure()
    print(f)
    f.plotBarChart([1,2,3])
    # f.show()
    f.show(False)

