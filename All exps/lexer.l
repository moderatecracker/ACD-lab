%option noyywrap

%{
    #include <stdio.h>
    extern FILE *yyin;  // Declare input file pointer
    int k = 0; // Counter for keywords
%}

%%

int|float|char   { 
    k++; 
    printf("Keyword found: %s\n", yytext);
    
    }

.|\n  { /* Ignore other characters */ }

%%

int main() {
    yyin = fopen("input.txt", "r");  // Open input file
    if (!yyin) {
        printf("Error: Unable to open file input.txt\n");
        return 1;
    }

    yylex();  // Start lexical analysis

    printf("Total keywords found: %d\n", k);
    
    fclose(yyin);  // Close file
    return 0;
}
