import tkinter as tk
from tkinter import ttk, scrolledtext
import ast

# Проверка синтаксиса
def validate_code(code):
    try:
        compile(code, "<string>", "exec")
        return True, ""
    except SyntaxError as e:
        return False, f"Синтаксическая ошибка: {e}"

# Парсим AST
class CodeNode:
    def __init__(self, node):
        self.node = node

    def __eq__(self, other):
        return ast.dump(self.node) == ast.dump(other.node)

# Получаем список выражений
def get_nodes(code):
    try:
        tree = ast.parse(code)
        return tree.body
    except:
        return []

# Слияние на основе AST
def merge_codes(code1, code2):
    nodes1 = get_nodes(code1)
    nodes2 = get_nodes(code2)

    merged_nodes = []
    green_indices = []

    # Хэшируем узлы из code1 для быстрого поиска
    existing_hashes = set(ast.dump(node) for node in nodes1)

    # Добавляем все узлы из code2
    for node in nodes2:
        key = ast.dump(node)
        if key not in existing_hashes:
            # Это новое выражение — добавляем зелёным
            merged_nodes.append(node)
            green_indices.append(len(merged_nodes) - 1)
        else:
            merged_nodes.append(node)

    # Добавляем всё из code1, если ещё не добавлено
    added_hashes = [ast.dump(n) for n in merged_nodes]
    for node in nodes1:
        key = ast.dump(node)
        if key not in added_hashes:
            merged_nodes.append(node)

    # Конвертируем AST обратно в текст
    lines = []
    green_lines = []

    merged_code = ""
    for i, node in enumerate(merged_nodes):
        line = ast.unparse(node)
        merged_code += line + "\n"
        if i in green_indices:
            green_lines.append(len(lines))
        lines.append(line)

    return merged_code.strip(), green_lines, []

# Обработчик кнопки слияния
def on_merge():
    code1 = tab1_text.get("1.0", tk.END)
    code2 = tab2_text.get("1.0", tk.END)

    valid1, msg1 = validate_code(code1)
    valid2, msg2 = validate_code(code2)

    if not valid1:
        result_label.config(text="Ошибка в Код 1: " + msg1)
        return
    if not valid2:
        result_label.config(text="Ошибка в Код 2: " + msg2)
        return

    result_label.config(text="Коды корректны.")

    merged_code, green, yellow = merge_codes(code1, code2)

    # Вкладка 3: объединённый код с подцветкой
    tab3 = scrolledtext.ScrolledText(notebook, wrap=tk.WORD)
    notebook.add(tab3, text="Вкладка 3: Объединённый код")
    tab3.delete("1.0", tk.END)
    tab3.insert(tk.END, merged_code)

    tab3.tag_configure("green", background="lightgreen")

    lines = merged_code.split('\n')
    for i in range(len(lines)):
        start = f"{i+1}.{0}"
        end = f"{i+1}.{len(lines[i])}"
        if i in green:
            tab3.tag_add("green", start, end)

    # Вкладка 4: готовый код
    tab4 = scrolledtext.ScrolledText(notebook, wrap=tk.WORD)
    notebook.add(tab4, text="Вкладка 4: Готовый код")
    tab4.insert(tk.END, merged_code)

# GUI
root = tk.Tk()
root.title("Мерджер кодов")

notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

tab1_text = scrolledtext.ScrolledText(notebook, wrap=tk.WORD)
notebook.add(tab1_text, text="Вкладка 1: Новый код")

tab2_text = scrolledtext.ScrolledText(notebook, wrap=tk.WORD)
notebook.add(tab2_text, text="Вкладка 2: Старый код")

result_label = tk.Label(root, text="", fg="blue")
result_label.pack(pady=5)

merge_button = tk.Button(root, text="Слить коды", command=on_merge)
merge_button.pack(pady=10)

root.mainloop()
