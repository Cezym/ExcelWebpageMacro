from ExcelSheetMacro import ExcelSheetMacro
from Interpreter import Interpreter
from WebpageMacro import WebpageMacro


class WebPageToExcelDataMacro(Interpreter):
    def __init__(self):
        super().__init__()
        self.web = WebpageMacro()
        self.exc = ExcelSheetMacro()
        self.interpretations = self.web.interpretations
        self.interpretations.update(self.exc.interpretations)
        self.interpretations["save_cell"] = self.save_cell
        self.interpretations["get_cell"] = self.save_cell
        self.interpretations["if"] = self.if_cond

    def save_cell(self, column, row, *value_parts):
        if len(value_parts) == 1:
            value = value_parts[0]
        else:
            value = self.exec_parts(list(value_parts))
        if isinstance(column, str):
            column = self.exc.data_table.labels[column]
        self.exc.worksheet.cell(row+1, column+1, value)
        self.exc.workbook.save(self.exc.path)
        self.exc.data_table.data[row][column] = value

    def get_cell(self, column, row):
        return self.exc.data_table[column][row]

    def exec_line_for_row(self, command, row_num):
        parts = Interpreter.split_line(command)
        if parts[0] in ["get_cell", "save_cell"]:
            parts = parts[:1]+[str(row_num)]+parts[2:]
        print(self.exec_parts(parts))


if __name__ == "__main__":
    wem = WebPageToExcelDataMacro()
    print(wem.interpretations.keys())
    inp: str = ""
    while inp != "STOP":
        #try:
            inp = input()
            print(wem.exec_line(inp))
        #except Exception as e:
        #    print(e)
