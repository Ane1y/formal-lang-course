grammar Grammar;
// Operators
DEL : ';';
ASSIGN : '=';
LP : '(';
RP : ')';
AND : '&';
OR : '|';
ARROW : '->';
KLEENE : '*';
TRANS : '<<';
CONCAT: '++';

// Keywords
MAP : 'map';
FILTER : 'filter';
VAR : 'var';
PRINT : 'print';
OF : 'of';
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


INT: [0-9]+;
SET: '{' '}' | '{' ELEM (',' ELEM)* '}';
ELEM: INT | INT '..' INT;
QUOTES: '"';
IDENT : [a-zA-Z_][a-zA-Z_0-9]*;
STRING: QUOTES (IDENT | INT | ' ' | '.')* QUOTES;
SPACE : [ \r\t\n]+ -> skip;


prog : (stmt DEL)* EOF;
stmt : bind | print | expr;

bind : VAR var ASSIGN expr;
print : PRINT expr;

var : IDENT;
val : INT | STRING | SET;

pattern : var | LP pattern (',' pattern)* RP;
lambda : pattern ARROW expr | LP lambda RP;

expr : LP expr RP
  | var
  | val
  | MAP lambda expr
  | FILTER lambda expr
  | expr AND expr                  // пересечение языков
  | expr OR expr                  // объединение языков
  | expr CONCAT expr                 // конкатенация
  | expr KLEENE
  | expr TRANS expr
  | SET_START expr OF  expr
  | SET_FINAL expr OF expr
  | ADD_START expr OF expr
  | ADD_FINALS expr OF expr
  | GET_START expr
  | GET_FINAL expr
  | GET_REACHABLE expr
  | GET_VERTICES expr
  | GET_EDGES expr
  | GET_LABELS expr
  | LOAD STRING;
