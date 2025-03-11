import tkinter as tk
from tkinter import messagebox
from collections import defaultdict

def generate_input_fields():
    try:
        count = int(num_productions_entry.get())
        if count <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number of productions")
        return
    
    for widget in grammar_frame.winfo_children():
        widget.destroy()
    
    global grammar_entries
    grammar_entries = []
    
    for i in range(count):
        label = tk.Label(grammar_frame, text=f"Production {i+1}:")
        label.pack()
        entry = tk.Entry(grammar_frame, width=50)
        entry.pack()
        grammar_entries.append(entry)

def normal_production():
    grammar = [entry.get() for entry in grammar_entries if entry.get()]
    output_text.set("\n".join(grammar) if grammar else "No grammar entered")

def compute_first():
    grammar = [entry.get() for entry in grammar_entries if entry.get()]
    first_sets = compute_first_sets(grammar)
    output_text.set("FIRST sets:\n" + "\n".join(f"FIRST({key}) = {value}" for key, value in first_sets.items()))

def compute_follow():
    grammar = [entry.get() for entry in grammar_entries if entry.get()]
    first_sets = compute_first_sets(grammar)
    follow_sets = compute_follow_sets(grammar, first_sets)
    output_text.set("FOLLOW sets:\n" + "\n".join(f"FOLLOW({key}) = {value}" for key, value in follow_sets.items()))

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

def process_cfg():
    """Processes the CFG by eliminating left recursion and performing left factoring."""
    grammar = [entry.get() for entry in grammar_entries if entry.get()]
    if not grammar:
        output_text.set("No grammar entered")
        return
    
    transformed_grammar = compute_cfg(grammar)

    output_text.set("Final Transformed CFG:\n" + "\n".join(transformed_grammar))

def compute_cfg(grammar):
    """Processes the CFG by eliminating left recursion and left factoring."""
    grammar = eliminate_left_recursion(grammar)
    grammar = left_factor(grammar)
    return grammar

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
    
    # Format output
    for non_terminal in first:
        print(f"First({non_terminal}) = {{ {', '.join(first[non_terminal])} }}")
    return first

def compute_follow_sets(grammar, first_sets):
    follow = defaultdict(set)
    rules = {rule.split("->")[0].strip(): rule.split("->")[1].strip().split("|") for rule in grammar}

    # Start symbol should have "$" in its FOLLOW set
    start_symbol = next(iter(rules))  # Get the first non-terminal as start symbol
    follow[start_symbol].add("$")

    changed = True
    while changed:
        changed = False
        for non_terminal, productions in rules.items():
            for production in productions:
                trailer = follow[non_terminal].copy()  # Initialize trailer as FOLLOW of LHS
                
                for i in reversed(range(len(production.split()))):
                    symbol = production.split()[i]

                    if symbol in rules:  # If symbol is a non-terminal
                        original_size = len(follow[symbol])
                        follow[symbol] |= trailer  # Add trailer to FOLLOW(symbol)

                        # If symbol has ε in its FIRST set, update trailer
                        if 'ε' in first_sets[symbol]:
                            trailer |= (first_sets[symbol] - {'ε'})
                        else:
                            trailer = first_sets[symbol]

                        # Check if FOLLOW set changed
                        if len(follow[symbol]) > original_size:
                            changed = True
                    else:
                        trailer = first_sets[symbol] if symbol in first_sets else {symbol}  # Terminal case
    # Format output
    for non_terminal in follow:
        print(f"Follow({non_terminal}) = {{ {', '.join(follow[non_terminal])} }}")

    return follow


# GUI Setup
root = tk.Tk()
root.title("Grammar Processor")
root.geometry("500x600")

tk.Label(root, text="Enter number of productions:").pack()
num_productions_entry = tk.Entry(root)
num_productions_entry.pack()
tk.Button(root, text="Generate Fields", command=generate_input_fields).pack()

grammar_frame = tk.Frame(root)
grammar_frame.pack()

buttons_frame = tk.Frame(root)
buttons_frame.pack()

tk.Button(buttons_frame, text="Compute LL(1)", command=compute_ll1).grid(row=0, column=1)
tk.Button(buttons_frame, text="Compute CFG", command=process_cfg).grid(row=1, column=0)
tk.Button(buttons_frame, text="Compute FIRST()", command=compute_first).grid(row=1, column=1)
tk.Button(buttons_frame, text="Compute FOLLOW()", command=compute_follow).grid(row=2, column=0, columnspan=2)

output_text = tk.StringVar()
output_label = tk.Label(root, textvariable=output_text, fg="blue")
output_label.pack()

root.mainloop()
