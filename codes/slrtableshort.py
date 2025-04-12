from collections import defaultdict, deque

# Grammar definition
grammar = {
    "S'": ["S"],
    "S": ["CC"],
    "C": ["cC", "d"]
}

terminals = {'c', 'd', '$'}
non_terminals = set(grammar.keys())

# Compute FIRST sets
def compute_first():
    first = defaultdict(set)
    changed = True
    while changed:
        changed = False
        for head in grammar:
            for prod in grammar[head]:
                for symbol in prod:
                    before = len(first[head])
                    first[head] |= first[symbol] if symbol in non_terminals else {symbol}
                    if before != len(first[head]):
                        changed = True
                    if symbol not in non_terminals or '' not in first[symbol]:
                        break
    return first

# Compute FOLLOW sets
def compute_follow(first):
    follow = defaultdict(set)
    follow["S'"].add('$')
    changed = True
    while changed:
        changed = False
        for head in grammar:
            for prod in grammar[head]:
                trailer = follow[head].copy()
                for symbol in reversed(prod):
                    if symbol in non_terminals:
                        before = len(follow[symbol])
                        follow[symbol] |= trailer
                        if before != len(follow[symbol]):
                            changed = True
                        if '' in first[symbol]:
                            trailer |= first[symbol] - {''}
                        else:
                            trailer = first[symbol]
                    else:
                        trailer = {symbol}
    return follow

# Closure function
def closure(items):
    closure_set = set(items)
    added = True
    while added:
        added = False
        new_items = set()
        for lhs, rhs, dot_pos in closure_set:
            if dot_pos < len(rhs) and rhs[dot_pos] in non_terminals:
                B = rhs[dot_pos]
                for prod in grammar[B]:
                    item = (B, prod, 0)
                    if item not in closure_set:
                        new_items.add(item)
                        added = True
        closure_set |= new_items
    return frozenset(closure_set)

# GOTO function
def goto(items, symbol):
    moved = {(lhs, rhs, dot+1) for (lhs, rhs, dot) in items if dot < len(rhs) and rhs[dot] == symbol}
    return closure(moved) if moved else frozenset()

# Build canonical collection of LR(0) items
def items():
    C = []
    init = closure([("S'", grammar["S'"][0], 0)])
    C.append(init)
    queue = deque([init])
    transitions = {}

    while queue:
        I = queue.popleft()
        for X in terminals | non_terminals:
            goto_I = goto(I, X)
            if goto_I and goto_I not in C:
                C.append(goto_I)
                queue.append(goto_I)
            if goto_I:
                transitions[(I, X)] = goto_I
    return C, transitions

# Build SLR parsing table
def build_slr_table(C, transitions, follow):
    action = {}
    goto_table = {}

    state_map = {state: i for i, state in enumerate(C)}

    for i, I in enumerate(C):
        for item in I:
            lhs, rhs, dot = item
            if dot < len(rhs):
                a = rhs[dot]
                if a in terminals:
                    j = state_map[transitions[(I, a)]]
                    action[(i, a)] = ("shift", j)
            else:
                if lhs != "S'":
                    for a in follow[lhs]:
                        action[(i, a)] = ("reduce", f"{lhs} -> {rhs}")
                else:
                    action[(i, '$')] = ("accept",)

        for A in non_terminals:
            if (I, A) in transitions:
                j = state_map[transitions[(I, A)]]
                goto_table[(i, A)] = j

    return action, goto_table

# Run it
first = compute_first()
follow = compute_follow(first)
C, transitions = items()
action, goto_table = build_slr_table(C, transitions, follow)

# Display
print("ACTION TABLE:")
for k, v in sorted(action.items()):
    print(f"{k}: {v}")
print("\nGOTO TABLE:")
for k, v in sorted(goto_table.items()):
    print(f"{k}: {v}")
