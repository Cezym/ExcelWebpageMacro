from WebPageToExcelDataMacro import WebPageToExcelDataMacro


class WebPageSheetManager:
    def __init__(self, sheet_path: str, script_path: str):
        self.web_page_sheet_macro: WebPageToExcelDataMacro = WebPageToExcelDataMacro()
        self.web_page_sheet_macro.exc.open_sheet(sheet_path)
        last_row = len(self.web_page_sheet_macro.exc.data_table.get(column=0))
        print(self.web_page_sheet_macro.exc.data_table)
        print(self.web_page_sheet_macro.exc.data_table.labels)
        print(last_row, "x", len(self.web_page_sheet_macro.exc.data_table.get(row=0)))
        with open(script_path) as file:
            self.commands = [line.strip() for line in file.readlines()]
        print(self.commands)

    def exec(self, excepts: list[int] = [], only: list[int] = None):
        if only:
            for idx in only:
                self.exec_row_num(idx)
            exit()
            return

        if len(excepts) == 0:
            for idx in range(1, len(self.web_page_sheet_macro.exc.data_table.get(column=0))):
                self.exec_row_num(idx)
        else:
            for idx in range(1, len(self.web_page_sheet_macro.exc.data_table.get(column=0))):
                if idx not in excepts:
                    self.exec_row_num(idx)
        exit()
        return

    def exec_row_num(self, row_num):
        for command in self.commands:
            self.web_page_sheet_macro.exec_line_for_row(command, row_num)


if __name__ == "__main__":
    wpsm = WebPageSheetManager("ExampleData.xlsx", "ExampleScript.txt")
    wpsm.exec()
