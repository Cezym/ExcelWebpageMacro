import function
import nltk


class Interpreter:
    conversion_dict = {
        "int": lambda a: int(a),
        "float": lambda a: float(a),
        "list": lambda a: list(a),
        "list[]": lambda a: Interpreter.to_list(a),
        "list][": lambda a: Interpreter.to_list(a, False),
    }

    def __init__(self, case_sensitive: bool = False):
        self.interpretations = {str: function}
        self.interpretations["if"] = self.if_cond
        self.case_sensitive = case_sensitive

    def add_interpretation(self, interpretation: ([str], [function])):
        self.interpretations[interpretation[0]] = interpretation[1]

    def __add__(self, other):
        if isinstance(([str], [function]), other):
            self.add_interpretation(other)

    def __sizeof__(self):
        return len(self.interpretations)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.interpretations)

    def __len__(self):
        return len(self.interpretations)

    def __setitem__(self, key: str, value):
        if self.case_sensitive:
            key = key.lower()
        self.interpretations[key] = value

    def __getitem__(self, item):
        if isinstance(item, str):
            return self.interpretations[item]

    def exec(self, command: str, *args):
        if len(args) != 0:
            return self.interpretations.get(command, None)(*args)

        return self.interpretations.get(command, None)()

    def exec_line(self, text: str):
        # print("L:", text)
        return self.exec_parts(Interpreter.split_line(text))

    def __exec_line_s(self, line: str):
        is_var = False
        is_var_c = ""
        part = ""
        parts: list[str] = []
        for c in line:
            part += c

            if c in ["\'", "[", "]"]:
                if is_var_c == "":
                    is_var = not is_var
                    is_var_c = c
                elif is_var_c == c or is_var_c == "[" and c == "]":
                    is_var = not is_var
                    is_var_c = ""

            if not is_var and c == " ":
                parts.append(part[:-1])
                part = ""

        parts.append(part)
        parts = Interpreter.try_to_convert(parts)
        return self.exec(parts[0], *parts[1:])

    @staticmethod
    def split_line(text: str):
        parts = []
        part = ""
        is_var = ""
        for char in text:
            part += char

            if char == "\"" or char == "'":
                if char == is_var:
                    is_var = ""
                else:
                    is_var = char

            if not is_var and char == " ":
                parts.append(part[:-1])
                part = ""
        parts.append(part)
        return parts

    @staticmethod
    def try_to_convert(parts: list[str]):
        ans = [parts[0]]
        for part in parts[1:]:
            if part.startswith("'") and part.endswith("'"):
                ans.append(part[1:-1])
            elif part[0] == "[" and "]" == part[-1]:
                ans.append(Interpreter.to_list(part))
            elif "." in part:
                ans.append(float(part))
            else:
                ans.append(int(part))
        return ans

    @staticmethod
    def to_list(a: str, has_brackets=True):
        ans = []
        a = a[1:-1] if has_brackets else a
        is_var = False
        part = ""
        parts: list[str] = []
        for c in a:
            part += c

            if c == "'":
                is_var = not is_var

            if not is_var and c == ",":
                parts.append(part[:-1])
                part = ""

            if part == " " and not is_var:
                part = part[:-1]
        parts.append(part)
        for part in parts:
            if part.startswith("'") and part.endswith("'"):
                ans.append(part[1:-1])
            elif "." in part:
                ans.append(float(part))
            else:
                ans.append(int(part))
        return ans

    @staticmethod
    def is_num(value: str, *classes):
        for clazz in classes:
            try:
                if clazz == int:
                    int(value)
                    return True
                elif clazz == float:
                    float(value)
                    return True
                return True
            except ValueError:
                return False
        return False

    @staticmethod
    def try_conv_to_num(value: str):
        try:
            if (value.startswith("\"") and value.endswith("\"")) or (value.startswith("'") and value.endswith("'")):
                return value[1:-1]
            try:
                return int(value)
            except ValueError:
                try:
                    return float(value)
                except ValueError:
                    return value
        except AttributeError:
            return value

    def exec_parts(self, parts: list[str]):
        # print("P:", parts)
        command, args = parts[0], parts[1:]
        if self.case_sensitive:
            command = command.lower()
        args = Interpreter.convert_all(args)
        args = [Interpreter.try_conv_to_num(arg) for arg in args]
        # args = [self.try_exec_line(part) for part in args for key in self.interpretations.keys() if key in part]
        # print("C:", command, "A:", args)
        # print(self.interpretations.keys())
        if command in self.interpretations.keys():
            # print("FOUND:", command)
            # func_arg_len = len(signature(self.interpretations[command]).parameters)
            # if func_arg_len != len(args):
            #     args = args[:func_arg_len-1] + [self.exec_parts(args[func_arg_len-1:])]
            #
            return self.interpretations[command](*args)

        else:
            return " ".join([str(part) for part in parts])

    @staticmethod
    def convert_all(args):
        arg: str
        ans = []
        for arg in args:
            try:
                was_in_conv = False
                for typ in Interpreter.conversion_dict.keys():
                    pre = "*" + typ + "*"
                    if arg.startswith(pre):
                        ans.append(Interpreter.conversion_dict[typ](arg[len(pre):]))
                        was_in_conv = True
                if not was_in_conv:
                    ans.append(arg)
            except AttributeError:
                ans.append(arg)

        return ans

    @staticmethod
    def split_list(l: list, split: str):
        for s in l:
            if s == split:
                return l[:l.index(s)], l[l.index(s) + 1:]
        return None

    def if_cond(self, *parts):
        condition, statement = None, None

        for then in ["->", "=>", "then"]:
            if then in parts:
                condition, statement = Interpreter.split_list(list(parts), then)
                break

        if not condition or not statement:
            raise ValueError("No then in if statement")

        conditions: list = [0, 0]

        operators = {
            "=": lambda a, b: a == b,
            "<": lambda a, b: a < b,
            ">": lambda a, b: a > b
        }
        operator = ""
        for operator in operators.keys():
            if operator in condition:
                conditions = [0, 0]
                conditions[0], conditions[1] = Interpreter.split_list(condition, operator)
                break

        if not conditions:
            raise ValueError("No then in if statement")

        if operators[operator](self.exec_parts(conditions[0]), self.exec_parts(conditions[1])):
            self.exec_parts(statement)

    @staticmethod
    def levenstein(a: str, b: str) -> int:
        return nltk.edit_distance(a, b)

    def try_exec_line(self, line: str):
        try:
            return self.exec_line(line)
        except Exception:
            return line


if __name__ == "__main__":
    interpreter = Interpreter()
    print_ = lambda a: print(a)
    sum_ = lambda *x: sum(x)
    interpreter["print"] = print_
    interpreter["sum"] = sum_

    interpreter.exec_line("print 'abc asd'")
    print(Interpreter.is_num("abc", int))
    print(interpreter.exec_line("sum 123 10 2"))
