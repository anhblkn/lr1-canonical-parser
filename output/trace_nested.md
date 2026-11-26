Input: `for ( init ; id ; step ) for ( init ; id ; step ) stmt eof`

| Step | Operation or lookup | Stack AFTER (bottom to top) | Remaining input AFTER | Pending or pushed AST value |
|---|---|---|---|---|
| 0 | Initialize | `$/CC0` | `for ( init ; id ; step ) for ( init ; id ; step ) stmt eof` | None |
| 1 | Shift for, go to CC2 | `$/CC0 for/CC2` | `( init ; id ; step ) for ( init ; id ; step ) stmt eof` | None |
| 2 | Shift (, go to CC4 | `$/CC0 for/CC2 (/CC4` | `init ; id ; step ) for ( init ; id ; step ) stmt eof` | None |
| 3 | Shift init, go to CC6 | `$/CC0 for/CC2 (/CC4 init/CC6` | `; id ; step ) for ( init ; id ; step ) stmt eof` | None |
| 4 | Reduce r3: I → init (lookahead ;) | `$/CC0 for/CC2 (/CC4` | `; id ; step ) for ( init ; id ; step ) stmt eof` | pending I1 = Init(init) |
| 5 | GOTO(CC4, I) = CC5 | `$/CC0 for/CC2 (/CC4 I/CC5` | `; id ; step ) for ( init ; id ; step ) stmt eof` | pushed I1 |
| 6 | Shift ;, go to CC7 | `$/CC0 for/CC2 (/CC4 I/CC5 ;/CC7` | `id ; step ) for ( init ; id ; step ) stmt eof` | None |
| 7 | Shift id, go to CC9 | `$/CC0 for/CC2 (/CC4 I/CC5 ;/CC7 id/CC9` | `; step ) for ( init ; id ; step ) stmt eof` | None |
| 8 | Reduce r4: C → id (lookahead ;) | `$/CC0 for/CC2 (/CC4 I/CC5 ;/CC7` | `; step ) for ( init ; id ; step ) stmt eof` | pending C1 = Identifier(id) |
| 9 | GOTO(CC7, C) = CC8 | `$/CC0 for/CC2 (/CC4 I/CC5 ;/CC7 C/CC8` | `; step ) for ( init ; id ; step ) stmt eof` | pushed C1 |
| 10 | Shift ;, go to CC10 | `$/CC0 for/CC2 (/CC4 I/CC5 ;/CC7 C/CC8 ;/CC10` | `step ) for ( init ; id ; step ) stmt eof` | None |
| 11 | Shift step, go to CC12 | `$/CC0 for/CC2 (/CC4 I/CC5 ;/CC7 C/CC8 ;/CC10 step/CC12` | `) for ( init ; id ; step ) stmt eof` | None |
| 12 | Reduce r5: U → step (lookahead )) | `$/CC0 for/CC2 (/CC4 I/CC5 ;/CC7 C/CC8 ;/CC10` | `) for ( init ; id ; step ) stmt eof` | pending U1 = Update(step) |
| 13 | GOTO(CC10, U) = CC11 | `$/CC0 for/CC2 (/CC4 I/CC5 ;/CC7 C/CC8 ;/CC10 U/CC11` | `) for ( init ; id ; step ) stmt eof` | pushed U1 |
| 14 | Shift ), go to CC13 | `$/CC0 for/CC2 (/CC4 I/CC5 ;/CC7 C/CC8 ;/CC10 U/CC11 )/CC13` | `for ( init ; id ; step ) stmt eof` | None |
| 15 | Shift for, go to CC2 | `$/CC0 for/CC2 (/CC4 I/CC5 ;/CC7 C/CC8 ;/CC10 U/CC11 )/CC13 for/CC2` | `( init ; id ; step ) stmt eof` | None |
| 16 | Shift (, go to CC4 | `$/CC0 for/CC2 (/CC4 I/CC5 ;/CC7 C/CC8 ;/CC10 U/CC11 )/CC13 for/CC2 (/CC4` | `init ; id ; step ) stmt eof` | None |
| 17 | Shift init, go to CC6 | `$/CC0 for/CC2 (/CC4 I/CC5 ;/CC7 C/CC8 ;/CC10 U/CC11 )/CC13 for/CC2 (/CC4 init/CC6` | `; id ; step ) stmt eof` | None |
| 18 | Reduce r3: I → init (lookahead ;) | `$/CC0 for/CC2 (/CC4 I/CC5 ;/CC7 C/CC8 ;/CC10 U/CC11 )/CC13 for/CC2 (/CC4` | `; id ; step ) stmt eof` | pending I2 = Init(init) |
| 19 | GOTO(CC4, I) = CC5 | `$/CC0 for/CC2 (/CC4 I/CC5 ;/CC7 C/CC8 ;/CC10 U/CC11 )/CC13 for/CC2 (/CC4 I/CC5` | `; id ; step ) stmt eof` | pushed I2 |
| 20 | Shift ;, go to CC7 | `$/CC0 for/CC2 (/CC4 I/CC5 ;/CC7 C/CC8 ;/CC10 U/CC11 )/CC13 for/CC2 (/CC4 I/CC5 ;/CC7` | `id ; step ) stmt eof` | None |
| 21 | Shift id, go to CC9 | `$/CC0 for/CC2 (/CC4 I/CC5 ;/CC7 C/CC8 ;/CC10 U/CC11 )/CC13 for/CC2 (/CC4 I/CC5 ;/CC7 id/CC9` | `; step ) stmt eof` | None |
| 22 | Reduce r4: C → id (lookahead ;) | `$/CC0 for/CC2 (/CC4 I/CC5 ;/CC7 C/CC8 ;/CC10 U/CC11 )/CC13 for/CC2 (/CC4 I/CC5 ;/CC7` | `; step ) stmt eof` | pending C2 = Identifier(id) |
| 23 | GOTO(CC7, C) = CC8 | `$/CC0 for/CC2 (/CC4 I/CC5 ;/CC7 C/CC8 ;/CC10 U/CC11 )/CC13 for/CC2 (/CC4 I/CC5 ;/CC7 C/CC8` | `; step ) stmt eof` | pushed C2 |
| 24 | Shift ;, go to CC10 | `$/CC0 for/CC2 (/CC4 I/CC5 ;/CC7 C/CC8 ;/CC10 U/CC11 )/CC13 for/CC2 (/CC4 I/CC5 ;/CC7 C/CC8 ;/CC10` | `step ) stmt eof` | None |
| 25 | Shift step, go to CC12 | `$/CC0 for/CC2 (/CC4 I/CC5 ;/CC7 C/CC8 ;/CC10 U/CC11 )/CC13 for/CC2 (/CC4 I/CC5 ;/CC7 C/CC8 ;/CC10 step/CC12` | `) stmt eof` | None |
| 26 | Reduce r5: U → step (lookahead )) | `$/CC0 for/CC2 (/CC4 I/CC5 ;/CC7 C/CC8 ;/CC10 U/CC11 )/CC13 for/CC2 (/CC4 I/CC5 ;/CC7 C/CC8 ;/CC10` | `) stmt eof` | pending U2 = Update(step) |
| 27 | GOTO(CC10, U) = CC11 | `$/CC0 for/CC2 (/CC4 I/CC5 ;/CC7 C/CC8 ;/CC10 U/CC11 )/CC13 for/CC2 (/CC4 I/CC5 ;/CC7 C/CC8 ;/CC10 U/CC11` | `) stmt eof` | pushed U2 |
| 28 | Shift ), go to CC13 | `$/CC0 for/CC2 (/CC4 I/CC5 ;/CC7 C/CC8 ;/CC10 U/CC11 )/CC13 for/CC2 (/CC4 I/CC5 ;/CC7 C/CC8 ;/CC10 U/CC11 )/CC13` | `stmt eof` | None |
| 29 | Shift stmt, go to CC3 | `$/CC0 for/CC2 (/CC4 I/CC5 ;/CC7 C/CC8 ;/CC10 U/CC11 )/CC13 for/CC2 (/CC4 I/CC5 ;/CC7 C/CC8 ;/CC10 U/CC11 )/CC13 stmt/CC3` | `eof` | None |
| 30 | Reduce r2: S → stmt (lookahead eof) | `$/CC0 for/CC2 (/CC4 I/CC5 ;/CC7 C/CC8 ;/CC10 U/CC11 )/CC13 for/CC2 (/CC4 I/CC5 ;/CC7 C/CC8 ;/CC10 U/CC11 )/CC13` | `eof` | pending B1 = BasicStmt(stmt) |
| 31 | GOTO(CC13, S) = CC14 | `$/CC0 for/CC2 (/CC4 I/CC5 ;/CC7 C/CC8 ;/CC10 U/CC11 )/CC13 for/CC2 (/CC4 I/CC5 ;/CC7 C/CC8 ;/CC10 U/CC11 )/CC13 S/CC14` | `eof` | pushed B1 |
| 32 | Reduce r1: S → for ( I ; C ; U ) S (lookahead eof) | `$/CC0 for/CC2 (/CC4 I/CC5 ;/CC7 C/CC8 ;/CC10 U/CC11 )/CC13` | `eof` | pending F1 = For(I2, C2, U2, B1) |
| 33 | GOTO(CC13, S) = CC14 | `$/CC0 for/CC2 (/CC4 I/CC5 ;/CC7 C/CC8 ;/CC10 U/CC11 )/CC13 S/CC14` | `eof` | pushed F1 |
| 34 | Reduce r1: S → for ( I ; C ; U ) S (lookahead eof) | `$/CC0` | `eof` | pending F2 = For(I1, C1, U1, F1) |
| 35 | GOTO(CC0, S) = CC1 | `$/CC0 S/CC1` | `eof` | pushed F2 |
| 36 | Accept (ACTION[CC1, eof] = acc) | `$/CC0 S/CC1` | `eof` | root F2 = For(I1, C1, U1, F1) |

Final outcome: accept, root value: F2 = For(I1, C1, U1, F1)
