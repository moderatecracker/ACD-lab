# Function to generate Assembly-like Three Address Code (TAC)
def generate_tac(statements):
    tac = []
    for statement in statements:
        # Assuming the statement is in the format "var1 = var2 op var3"
        parts = statement.split()
        if len(parts) == 5:  # Format: var1 = var2 op var3
            var1, _, var2, op, var3 = parts
            
            # Generate TAC based on the operation
            if op == '+':
                tac.append(f"LOAD R1, {var2}")  # Load var2 into R1
                tac.append(f"ADD R1, {var3}")   # Add var3 to R1
                tac.append(f"STORE {var1}, R1") # Store the result in var1
            elif op == '-':
                tac.append(f"LOAD R1, {var2}")  # Load var2 into R1
                tac.append(f"SUB R1, {var3}")   # Subtract var3 from R1
                tac.append(f"STORE {var1}, R1") # Store the result in var1
            elif op == '*':
                tac.append(f"LOAD R1, {var2}")  # Load var2 into R1
                tac.append(f"MUL R1, {var3}")   # Multiply R1 by var3
                tac.append(f"STORE {var1}, R1") # Store the result in var1
            elif op == '/':
                tac.append(f"LOAD R1, {var2}")  # Load var2 into R1
                tac.append(f"DIV R1, {var3}")   # Divide R1 by var3
                tac.append(f"STORE {var1}, R1") # Store the result in var1
            else:
                print(f"Unsupported operation: {op}")  # Handle unsupported operations
        else:
            print(f"Invalid statement format: {statement}")  # Handle invalid formats
    return tac

# Function to generate Target Code
def target_code(tac):
    target = []
    for code in tac:
        target.append(f"Target: {code}")
    return target

# Input number of statements for TAC generation
num_statements = int(input("Enter the number of statements for TAC generation: "))
statements = []

# Input statements
for i in range(num_statements):
    statement = input(f"Enter statement {i + 1} (e.g., 'a = b + c'): ")
    statements.append(statement)

# Generate TAC
tac = generate_tac(statements)
print("\nGenerated Assembly-like Three Address Code (TAC):")
for code in tac:
    print(code)

# Generate and display Target Code
target = target_code(tac)
print("\nGenerated Target Code:")
for code in target:
    print(code)
