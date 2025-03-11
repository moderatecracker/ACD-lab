import tkinter as tk
from tkinter import messagebox, ttk
from collections import defaultdict

# Global variable to store input fields
grammar_entries = []

# Function to generate input fields
def generate_input_fields():
    global grammar_entries  
    try:
        count = int(num_productions_entry.get())
        if count <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number of productions")
        return

    # Clear previous fields
    for widget in grammar_frame.winfo_children():
        widget.destroy()

    grammar_entries = []  

    for i in range(count):
        label = tk.Label(grammar_frame, text=f"Production {i+1}:")
        label.grid(row=i, column=0, padx=5, pady=2, sticky='w')
        entry = tk.Entry(grammar_frame, width=50)
        entry.grid(row=i, column=1, padx=5, pady=2)
        grammar_entries.append(entry)  

# Process CFG
def process_cfg():
    grammar = [entry.get().strip() for entry in grammar_entries if entry.get().strip()]
    if not grammar:
        output_text.set("No grammar entered")
        return
    
    transformed_grammar = compute_cfg(grammar)
    output_text.set("Final Transformed CFG:\n" + "\n".join(transformed_grammar))

# Compute CFG
def compute_cfg(grammar):
    grammar = eliminate_left_recursion(grammar)
    grammar = left_factor(grammar)
    return grammar

# Eliminate Left Recursion
def eliminate_left_recursion(grammar):
    new_grammar = []
    for rule in grammar:
        lhs, rhs = rule.split("->")
        lhs = lhs.strip()
        rhs = [alt.strip() for alt in rhs.split("|")]
        recursive = [alt[1:].strip() for alt in rhs if alt.startswith(lhs)]
        non_recursive = [alt for alt in rhs if not alt.startswith(lhs)]
        if recursive:
            new_nt = lhs + "'"
            new_grammar.append(f"{lhs} -> " + " | ".join(f"{alt} {new_nt}" for alt in non_recursive))
            new_grammar.append(f"{new_nt} -> " + " | ".join(f"{alt} {new_nt}" for alt in recursive) + " | ε")
        else:
            new_grammar.append(rule)
    return new_grammar

# Left Factoring
def left_factor(grammar):
    new_grammar = []
    for rule in grammar:
        lhs, rhs = rule.split("->")
        lhs = lhs.strip()
        rhs = [alt.strip() for alt in rhs.split("|")]
        common_prefix = None
        for i in range(len(rhs) - 1):
            prefix = rhs[i].split()[0]
            if all(alt.startswith(prefix) for alt in rhs):
                common_prefix = prefix
                break
        if common_prefix:
            new_nt = lhs + "'"
            new_grammar.append(f"{lhs} -> {common_prefix} {new_nt}")
            new_grammar.append(f"{new_nt} -> " + " | ".join(alt[len(common_prefix):].strip() or "ε" for alt in rhs))
        else:
            new_grammar.append(rule)
    return new_grammar

# Compute FIRST sets
def compute_first_sets(grammar):
    first = defaultdict(set)
    rules = {rule.split("->")[0].strip(): rule.split("->")[1].strip().split("|") for rule in grammar}
    
    def first_of(symbol):
        if symbol in first:
            return first[symbol]
        if not symbol.isupper():
            return {symbol}
        for production in rules.get(symbol, []):
            for char in production.split():
                first[symbol] |= first_of(char)
                if 'ε' not in first_of(char):
                    break
        return first[symbol]
    
    for non_terminal in rules:
        first_of(non_terminal)
    
    return first

# Compute FOLLOW sets
def compute_follow_sets(grammar, first_sets):
    follow = defaultdict(set)
    rules = {rule.split("->")[0].strip(): rule.split("->")[1].strip().split("|") for rule in grammar}

    start_symbol = next(iter(rules))  
    follow[start_symbol].add("$")

    changed = True
    while changed:
        changed = False
        for non_terminal, productions in rules.items():
            for production in productions:
                trailer = follow[non_terminal].copy()
                
                for i in reversed(range(len(production.split()))):
                    symbol = production.split()[i]

                    if symbol in rules:  
                        original_size = len(follow[symbol])
                        follow[symbol] |= trailer  

                        if 'ε' in first_sets[symbol]:
                            trailer |= (first_sets[symbol] - {'ε'})
                        else:
                            trailer = first_sets[symbol]

                        if len(follow[symbol]) > original_size:
                            changed = True
                    else:
                        trailer = first_sets[symbol] if symbol in first_sets else {symbol}  
    return follow

# Display Parsing Table
def display_parsing_table(table):
    for widget in table_frame.winfo_children():
        widget.destroy()

    if not table:
        messagebox.showerror("Error", "Parsing table is empty or could not be generated")
        return

    terminals = sorted(set(term for rules in table.values() for term in rules))
    terminals.append("$")  # Add end-of-input symbol

    columns = ["Non-Terminal"] + terminals  # Ensure order
    tree = ttk.Treeview(table_frame, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor="center")

    for non_terminal, rules in table.items():
        row = [non_terminal] + [rules.get(col, "-") for col in terminals]
        tree.insert("", "end", values=row)

    tree.pack(expand=True, fill="both")

# Compute Parsing Table
def compute_parsing_table():
    global grammar_entries

    grammar = [entry.get() for entry in grammar_entries if entry.get()]
    if not grammar:
        output_text.set("No grammar entered")
        return

    grammar = eliminate_left_recursion(grammar)
    grammar = left_factor(grammar)
    
    first_sets = compute_first_sets(grammar)
    follow_sets = compute_follow_sets(grammar, first_sets)

    table, terminals = compute_parsing_table_logic(grammar, first_sets, follow_sets)

    display_parsing_table(table)

# Compute LL(1) Parsing Table Logic
def compute_parsing_table_logic(grammar, first, follow):
    parsing_table = {}
    rules = {rule.split("->")[0].strip(): rule.split("->")[1].strip().split("|") for rule in grammar}
    terminals = set()

    for productions in rules.values():
        for prod in productions:
            for symbol in prod.split():
                if symbol not in rules and symbol != "ε":
                    terminals.add(symbol)

    terminals = sorted(terminals)
    terminals.append("$")  # End of input marker

    for non_terminal in rules:
        parsing_table[non_terminal] = {t: "-" for t in terminals}  # Default empty

    for A in rules:
        for prod in rules[A]:
            first_set = set()
            prod_symbols = prod.split()

            # Compute FIRST for the production
            for symbol in prod_symbols:
                first_set |= (first[symbol] - {"ε"}) if symbol in first else {symbol}
                if "ε" not in first.get(symbol, {}):
                    break
            else:
                first_set.add("ε")

            # Fill table based on FIRST
            for terminal in first_set - {"ε"}:
                parsing_table[A][terminal] = prod

            # If epsilon is in FIRST, use FOLLOW(A)
            if "ε" in first_set:
                for terminal in follow[A]:
                    parsing_table[A][terminal] = "ε"

    return parsing_table, terminals

def check_ll1(grammar, first_sets, follow_sets):
    rules = {rule.split("->")[0].strip(): rule.split("->")[1].strip().split("|") for rule in grammar}
    ll1_grammar = []
    for non_terminal, productions in rules.items():
        first_seen = set()
        for production in productions:
            first_of_prod = set()
            for char in production.split():
                first_of_prod |= first_sets[char]
                if 'ε' not in first_sets[char]:
                    break
            if first_seen & first_of_prod:
                output_text.set("Grammar is NOT LL(1)")
                return
            first_seen |= first_of_prod
        ll1_grammar.append(f"{non_terminal} -> " + " | ".join(productions))
    output_text.set("LL(1) Grammar:\n" + "\n".join(ll1_grammar))

def compute_ll1():
    grammar = [entry.get() for entry in grammar_entries if entry.get()]
    grammar = eliminate_left_recursion(grammar)
    grammar = left_factor(grammar)
    first_sets = compute_first_sets(grammar)
    follow_sets = compute_follow_sets(grammar, first_sets)
    check_ll1(grammar, first_sets, follow_sets)

# GUI Setup
root = tk.Tk()
root.title("LL(1) Parser Generator")
root.geometry("800x600")

tk.Label(root, text="Enter number of productions:").pack()
num_productions_entry = tk.Entry(root)
num_productions_entry.pack()
tk.Button(root, text="Generate Fields", command=generate_input_fields).pack()

grammar_frame = tk.Frame(root)
grammar_frame.pack()

table_frame = tk.Frame(root)
table_frame.pack()

tk.Button(root, text="Compute LL(1)", command=compute_ll1).pack()
tk.Button(root, text="Compute CFG", command=process_cfg).pack()
tk.Button(root, text="Compute Parsing Table", command=compute_parsing_table).pack()

output_text = tk.StringVar()
tk.Label(root, textvariable=output_text, fg="blue").pack()

root.mainloop()
