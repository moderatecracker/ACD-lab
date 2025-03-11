%{
#include <stdio.h>
#include <stdlib.h>
void yyerror(const char *s);
int yylex();
%}

%token NUMBER
%left '+' '-'
%left '*' '/'
%right UMINUS

%%
expr: expr '+' expr
    | expr '-' expr
    | expr '*' expr
    | expr '/' expr
    | '(' expr ')'
    | '-' expr %prec UMINUS
    | NUMBER
    ;
%%

void yyerror(const char *s) {
    printf("Error: Invalid Expression\n");
}

int main() {
    printf("Enter an arithmetic expression:\n");
    if (yyparse() == 0) {  // yyparse() returns 0 if parsing is successful
        printf("Valid Expression\n");
    }
    return 0;
}