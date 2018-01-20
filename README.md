# Interpreter
A toy interpreter for an introductory course on compilers.

# Grammar:

Program --> Assignment*
    
Assignment --> Identifier = Exp;
    
Exp --> Exp + Term | Exp - Term | Term

Term --> Term * Fact | Term / Fact | Fact

Fact --> ( Exp ) | - Fact | + Fact | Literal | Identifier

Identifier --> Letter [Letter | Digit]*

Letter --> a|...|z|A|...|Z|_

Literal --> 0 | NonZeroDigit Digit*

NonZeroDigit --> 1|...|9

Digit --> 0|1|...|9
