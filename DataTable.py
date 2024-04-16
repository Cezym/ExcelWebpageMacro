from openpyxl.cell import Cell
from openpyxl.reader.excel import load_workbook
from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from tabulate import tabulate


class DataTable:
    def __init__(self):
        self.labels: dict[str, int] = None
        self.data: list[str] = None

    def __getitem__(self, col):
        if isinstance(col, str):
            if col in self.labels.keys():
                return [self.data[i][self.labels[col]] for i in range(len(self.data))]
            else:
                col = int(col)
        if isinstance(col, int):
            return [self.data[i][col] for i in range(len(self.data))]

    def __str__(self):
        return tabulate(self.data)

    def __repr__(self):
        print(str(self))

    @staticmethod
    def fromExcel(path):
        dt: DataTable = DataTable()
        workbook: Workbook = load_workbook(filename=path)
        worksheet: Worksheet = workbook.active
        dt.labels = {}
        dt.data = []
        cell: Cell
        for cell in list(worksheet.rows)[0]:
            dt.labels[cell.value] = cell.column - 1
        for row in worksheet.rows:
            r = []
            for cell in row:
                r.append(str(cell.value))
            dt.data.append(r)
        return dt

    def get(self, row:int = None, column:[int,str] = None):
        if row is not None and column is None:
            return self.data[row]
        elif row is None and column is not None:
            return self[column]
        elif row is not None and column is not None:
            return self[column][row]
