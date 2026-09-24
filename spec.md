# Loft — Language Specification

**Course:** Survey of Programming Languages — BYOL Term Project
**Status:** Week 1 — Language Specification & Lexical Analysis

## 1. Overview

Loft is a small, dynamically-typed toy language. It is deliberately
**Turing-incomplete**: there are no loops, no user-defined functions, and
no recursion, so every Loft program is guaranteed to terminate. What it
*does* support is enough to be genuinely useful as a teaching example:
variables, arithmetic, string handling, boolean logic, and single-level
`if / else` branching.

Design goals:
- **Readable** — keyword-based blocks (`then` / `end`) instead of braces
  or significant whitespace, so structure is visible without relying on
  indentation.
- **Small surface area** — 11 keywords, 13 operators, 3 literal types.
  Small enough to fully specify and implement in three weeks.
- **Predictable** — one clear operator-precedence table, no implicit
  type coercion except `+` doubling as string concatenation.

## 2. Data Types

| Type    | Example         | Notes                                           |
|---------|-----------------|--------------------------------------------------|
| Integer | `42`, `0`       | Whole numbers only, no decimals.                 |
| String  | `"hello"`       | Double-quoted. Supports `\n`, `\t`, `\"`, `\\`.  |
| Boolean | `true`, `false` | Produced by comparisons/logic; also literals.    |

There is no explicit type declaration — a variable's type is whatever
value it currently holds (dynamic typing).

## 3. Keywords

`let` `if` `then` `else` `end` `print` `and` `or` `not` `true` `false`

Keywords are reserved and cannot be used as variable names.

## 4. Operators (highest to lowest precedence)

| Precedence  | Operators                     | Associativity | Meaning                        |
|------------:|--------------------------------|---------------|----------------------------------|
| 1 (highest) | `( )`                          | —             | Grouping                        |
| 2           | unary `-`                      | right         | Negation                        |
| 3           | `*` `/` `%`                    | left          | Multiply, divide, modulo        |
| 4           | `+` `-`                        | left          | Add/concatenate, subtract       |
| 5           | `==` `!=` `<` `>` `<=` `>=`    | left          | Comparison (produce a boolean)  |
| 6           | `not`                          | right         | Logical NOT                     |
| 7           | `and`                          | left          | Logical AND                     |
| 8 (lowest)  | `or`                           | left          | Logical OR                      |

`+` is overloaded: `5 + 3` yields `8`, but `"a" + "b"` yields `"ab"`.
Mixing an integer and a string with `+` is a runtime error (checked by
the Week 3 evaluator, not the lexer).

Assignment (`=`) is not an expression operator — it only appears inside
a `let` statement.

## 5. Comments & Whitespace

- `#` starts a comment that runs to the end of the line.
- Spaces and tabs are insignificant except inside string literals.
- A newline ends a statement, so statements do not need a terminator
  like `;`.

## 6. Grammar (EBNF)

```
program        = { statement } ;

statement      = let_stmt | if_stmt | print_stmt ;

let_stmt       = "let" , identifier , "=" , expression ;

if_stmt        = "if" , expression , "then" ,
                  { statement } ,
                  [ "else" , { statement } ] ,
                  "end" ;

print_stmt     = "print" , expression ;

expression     = or_expr ;
or_expr        = and_expr , { "or" , and_expr } ;
and_expr       = not_expr , { "and" , not_expr } ;
not_expr       = [ "not" ] , comparison ;
comparison     = arithmetic , [ comp_op , arithmetic ] ;
comp_op        = "==" | "!=" | "<" | ">" | "<=" | ">=" ;
arithmetic     = term , { ( "+" | "-" ) , term } ;
term           = factor , { ( "*" | "/" | "%" ) , factor } ;
factor         = [ "-" ] , primary ;
primary        = integer | string | "true" | "false"
                | identifier | "(" , expression , ")" ;

identifier     = letter , { letter | digit | "_" } ;
integer        = digit , { digit } ;
string         = '"' , { character } , '"' ;
letter         = "a" | "b" | ... | "z" | "A" | ... | "Z" ;
digit          = "0" | "1" | ... | "9" ;
```

*Note: `if_stmt` only defines one `else` branch, but since `statement`
is recursive, putting a nested `if` inside that `else` branch gives
`else if` chains for free — no extra grammar rule needed.*

## 7. Example Programs

### 7.1 Arithmetic — rectangle area
```
# compute area of a rectangle
let width = 6
let height = 3
let area = width * height
print area
```

### 7.2 String concatenation
```
let first = "Loft"
let second = "Lang"
let full = first + second
print full
```

### 7.3 Conditional branching
```
let score = 82
if score >= 60 then
    print "pass"
else
    print "fail"
end
```

### 7.4 Logical operators + condition
```
let a = 10
let b = 20
if a < b and b < 100 then
    print "in range"
else
    print "out of range"
end
```

### 7.5 Sequence of calculations
```
let n = 5
let doubled = n * 2
let squared = n * n
print doubled
print squared
```

## 8. Error Handling

The lexer never lets a malformed source file crash the interpreter with
a raw traceback. Any illegal character, unterminated string, or bad
escape sequence raises a `LexerError` carrying the offending line and
column, which `main.py` (Week 3) will catch and print as a clean
diagnostic.

## 9. Why Turing-Incomplete?

Loft has no loop construct and no recursion (no user-defined functions
at all), so no Loft program can fail to terminate. This satisfies the
assignment's Turing-incompleteness requirement without artificial
restrictions — the language simply doesn't need loops to demonstrate
lexing, parsing, and evaluation.
