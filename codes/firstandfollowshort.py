from collections import defaultdict

grammar = defaultdict(list)
first, follow = defaultdict(set), defaultdict(set)

def compute_first(X):
    if X in first and first[X]: return first[X]
    if not X.isupper(): return {X}
    for prod in grammar[X]:
        for sym in prod:
            sym_first = compute_first(sym)
            first[X] |= sym_first - {'ε'}
            if 'ε' not in sym_first: break
        else: first[X].add('ε')
    return first[X]

def compute_follow(start):
    follow[start].add('$')
    updated = True
    while updated:
        updated = False
        for lhs in grammar:
            for prod in grammar[lhs]:
                for i, B in enumerate(prod):
                    if B.isupper():
                        trailer = prod[i+1:]
                        temp = set()
                        for sym in trailer:
                            sym_first = compute_first(sym)
                            temp |= sym_first - {'ε'}
                            if 'ε' not in sym_first: break
                        else: temp |= follow[lhs]
                        if not temp <= follow[B]:
                            follow[B] |= temp
                            updated = True

def input_grammar():
    for _ in range(int(input("No. of productions: "))):
        line = input().strip()
        if '->' not in line:
            print("Invalid production:", line)
            continue
        lhs, rhs = line.split("->")
        for alt in rhs.split('|'):
            grammar[lhs.strip()].append(alt.strip().split())

# Main
input_grammar()
start = list(grammar.keys())[0]
for nt in grammar: compute_first(nt)
compute_follow(start)

print("\nFIRST sets:")
for nt in grammar: print(f"FIRST({nt}) = {{ {', '.join(first[nt])} }}")
print("\nFOLLOW sets:")
for nt in grammar: print(f"FOLLOW({nt}) = {{ {', '.join(follow[nt])} }}")
