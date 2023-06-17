grammar Grammar;
// Operators
DEL : ';';
ASSIGN : '=';
LP : '(';
RP : ')';
AND : '&';
LC : '{';
RC : '}';
OR : '|';
ARROW : '->';
KLEENE : '*';
CONCAT: '++';
QUOTES: '"';
COMMA : ',';
// Keywords
MAP : 'map';
FILTER : 'filter';
VAR : 'var';
PRINT : 'print';
OF : 'of';
FA : 'fa';
SET_START : 'set_start';
SET_FINAL :'set_final';
ADD_START : 'add_start';
ADD_FINALS : 'add_finals';
GET_START: 'get_start';
GET_FINAL : 'get_final';
GET_REACHABLE : 'get_reachable';
GET_VERTICES : 'get_vertices';
GET_EDGES : 'get_edges';
GET_LABELS : 'get_labels';
LOAD : 'load';

literal: INT | STRING;

prog : (stmt DEL)* EOF;
stmt : bind | print_expr | expr | lambda_expr;

bind : VAR var ASSIGN expr;
print_expr : PRINT expr;
pattern : var | LP pattern (',' pattern)* RP;
lambda_expr : pattern ARROW expr | LP lambda_expr RP;

set: LC RC | LC setElem (COMMA setElem)* RC;
setElem: literal                    # setElemLiteral
        | literal '..' literal      # setElemRange;

var : IDENT;
val : literal | set;


expr : LP expr RP                   # exprParenthesis
  | var                             # exprVar
  | val                             # exprVal
  | MAP lambda_expr expr            # exprMap
  | FILTER lambda_expr expr         # exprFilter
  | expr AND expr                   # exprAnd
  | expr OR expr                    # exprOr
  | expr CONCAT expr                # exprConcat
  | expr KLEENE                     # exprKleene
  | SET_START expr OF  expr         # exprSetStart
  | SET_FINAL expr OF expr          # exprSetFinal
  | ADD_START expr OF expr          # exprAddStart
  | ADD_FINALS expr OF expr         # exprAddFinals
  | GET_START expr                  # exprGetStart
  | GET_FINAL expr                  # exprGetFinal
  | GET_REACHABLE expr              # exprGerReachable
  | GET_VERTICES expr               # exprGetVertices
  | GET_EDGES expr                  # exprGetEdges
  | GET_LABELS expr                 # exprGetLabels
  | LOAD STRING                     # exprLoad
  | FA literal                      # exprFiniteAutomata;


WS: [ \t\n\r\u000C] -> skip;
STRING: QUOTES (IDENT | INT | ' ' | '.')* QUOTES;

INT: [0-9]+;
IDENT : [a-zA-Z][a-zA-Z_0-9]*;

