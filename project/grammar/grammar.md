# Задача 13. Язык запросов к графам

## Описание абстрактного синтаксиса языка

```
prog = List<stmt>

stmt =
    bind of var * expr
  | print of expr

val =
    String of string
  | Int of int
  | Bool of bool
  | Graph of graph
  | Labels of labels
  | Edges of edges
  | Vertices of vertices

  
expr =
    Var of var                   // переменные
  | Val of val                   // константы
  | Set_start of Set<val> * expr // задать множество стартовых состояний
  | Set_final of Set<val> * expr // задать множество финальных состояний
  | Add_start of Set<val> * expr // добавить состояния в множество стартовых
  | Add_final of Set<val> * expr // добавить состояния в множество финальных
  | Get_start of expr            // получить множество стартовых состояний
  | Get_final of expr            // получить множество финальных состояний
  | Get_reachable of expr        // получить все пары достижимых вершин
  | Get_vertices of expr         // получить все вершины
  | Get_edges of expr            // получить все рёбра
  | Get_labels of expr           // получить все метки
  | Map of lambda * expr         // классический map
  | Filter of lambda * expr      // классический filter
  | Load of path                 // загрузка графа
  | Intersect of expr * expr     // пересечение языков
  | Concat of expr * expr        // конкатенация языков
  | Union of expr * expr         // объединение языков
  | Star of expr                 // замыкание языков (звезда Клини)
  | Smb of expr                  // единичный переход

lambda =
    Lambda of var * expr
```

## Конкретный синтаксис
```
prog -> (stmt DEL)* EOF
stmt: lind | print
bind: VAR var ASSIGN expr
print: PRINT expr

var: IDENT;
val: INT | STRING | SET

lambda: pattern '->' expr | '(' lambda ')'
pattern: var | '(' pattern (',' pattern)* ')'

expr =
    var
  | val
  | LP expr RP
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
  | GET_FINAL' expr
  | GET_REACHABLE expr
  | GET_VERTICES expr
  | GET_EDGES expr
  | GET_LABELS expr
  | LOAD STRING
    
DEL : ';'
ASSIGN : '='
IDENT : [a-zA-Z_][a-zA-Z_0-9]*
INT: [0-9]+
SET: '{' '}' | '{' ELEM (',' ELEM)* '}';
ELEM: INT | INT '..' INT;
QUOTES: '"'
STRING: QUOTES (IDENT | INT | ' ')* QUOTES
VAR : 'var'
PRINT : 'print'
LP : '('
RP : ')'
MAP : 'map'
FILTER : 'filter'
AND : '&'
OR : '|'
KLEENE : '*'
TRANS : '<<'

OF : of
SET_START : 'set_start'
SET_FINAL :'set_final'
ADD_START : 'add_start'
ADD_FINALS : 'add_finals'
GET_START: 'get_start'
GET_FINAL : 'get_final'
GET_REACHABLE : 'get_reachable'
GET_VERTICES : 'get_vertices'
GET_EDGES : 'get_edges'
GET_LABELS : 'get_labels'
LOAD : 'load'
```
## Примеры
Загрузить граф
```
var g = load "graph.dot"
```
Установить вершины 0..4 стартовыми
```
var g1 = set_start {0..4} of g ;
```
Установить все вершины финальными
```
var g2 = set_final set (get_vertices of g) of g1;
```
Получить первый элемент из пары достижимых вершин
```
var reachables = get_reachable g
var lst = map (a, b) -> a reachables
print lst
```

