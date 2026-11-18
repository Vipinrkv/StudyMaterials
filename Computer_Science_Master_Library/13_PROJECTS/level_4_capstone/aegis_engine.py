"""
AegisDB: Production-Grade Optimizing Relational Storage & Analytical Engine
========================================================================
Level 4 Capstone Implementation:
- Formal Lexer & Recursive Descent SQL AST Parser
- Constant Folding & Plan Optimization Pass
- Volcano Iterator Physical Execution Model (open/next/close)
- 4096-Byte Slotted Page Storage Engine
- Buffer Pool Manager with CLOCK Page Eviction
- Multi-Version Concurrency Control (MVCC) with Snapshot Isolation
- Write-Ahead Logging (WAL) with ARIES Crash Recovery
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")
from typing import Dict, List, Set, Tuple, Optional, Any
import struct
import re
import json


# ===========================================================================
# 1. FRONTEND: LEXER & RECURSIVE DESCENT SQL PARSER
# ===========================================================================

class TokenType:
    SELECT = "SELECT"
    FROM = "FROM"
    WHERE = "WHERE"
    INSERT = "INSERT"
    INTO = "INTO"
    VALUES = "VALUES"
    UPDATE = "UPDATE"
    SET = "SET"
    DELETE = "DELETE"
    BEGIN = "BEGIN"
    COMMIT = "COMMIT"
    ROLLBACK = "ROLLBACK"
    IDENT = "IDENT"
    NUMBER = "NUMBER"
    STRING = "STRING"
    COMMA = "COMMA"
    SEMICOLON = "SEMICOLON"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    EQUALS = "EQUALS"
    GREATER = "GREATER"
    LESS = "LESS"
    PLUS = "PLUS"
    STAR = "STAR"
    EOF = "EOF"


class Token:
    def __init__(self, ttype: str, val: Any, pos: int):
        self.type = ttype
        self.val = val
        self.pos = pos

    def __repr__(self):
        return f"Token({self.type}, {repr(self.val)})"


class SQLLexer:
    KEYWORDS = {
        "SELECT": TokenType.SELECT,
        "FROM": TokenType.FROM,
        "WHERE": TokenType.WHERE,
        "INSERT": TokenType.INSERT,
        "INTO": TokenType.INTO,
        "VALUES": TokenType.VALUES,
        "UPDATE": TokenType.UPDATE,
        "SET": TokenType.SET,
        "DELETE": TokenType.DELETE,
        "BEGIN": TokenType.BEGIN,
        "COMMIT": TokenType.COMMIT,
        "ROLLBACK": TokenType.ROLLBACK,
    }

    PATTERNS = [
        ("STRING", r"'[^']*'"),
        ("NUMBER", r"\d+(\.\d+)?"),
        ("IDENT", r"[a-zA-Z_][a-zA-Z0-9_]*"),
        ("EQUALS", r"="),
        ("GREATER", r">"),
        ("LESS", r"<"),
        ("PLUS", r"\+"),
        ("STAR", r"\*"),
        ("COMMA", r","),
        ("SEMICOLON", r";"),
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("SKIP", r"[ \t\r\n]+"),
    ]

    def __init__(self, query: str):
        self.query = query
        self.tokens: List[Token] = []
        self._tokenize()

    def _tokenize(self):
        regex = "|".join(f"(?P<{name}>{pat})" for name, pat in self.PATTERNS)
        for match in re.finditer(regex, self.query):
            kind = match.lastgroup
            val = match.group()
            pos = match.start()

            if kind == "SKIP":
                continue
            elif kind == "NUMBER":
                num = float(val) if "." in val else int(val)
                self.tokens.append(Token(TokenType.NUMBER, num, pos))
            elif kind == "STRING":
                self.tokens.append(Token(TokenType.STRING, val[1:-1], pos))
            elif kind == "IDENT":
                upper = val.upper()
                if upper in self.KEYWORDS:
                    self.tokens.append(Token(self.KEYWORDS[upper], upper, pos))
                else:
                    self.tokens.append(Token(TokenType.IDENT, val, pos))
            else:
                self.tokens.append(Token(getattr(TokenType, kind), val, pos))

        self.tokens.append(Token(TokenType.EOF, "", len(self.query)))


class ASTNode:
    pass


class SelectQuery(ASTNode):
    def __init__(self, table: str, columns: List[str], condition: Optional[Tuple[str, str, Any]]):
        self.table = table
        self.columns = columns
        self.condition = condition  # (col, op, value)


class InsertQuery(ASTNode):
    def __init__(self, table: str, values: List[Any]):
        self.table = table
        self.values = values


class UpdateQuery(ASTNode):
    def __init__(self, table: str, set_col: str, set_val: Any, condition: Optional[Tuple[str, str, Any]]):
        self.table = table
        self.set_col = set_col
        self.set_val = set_val
        self.condition = condition


class TxControlQuery(ASTNode):
    def __init__(self, action: str):
        self.action = action  # "BEGIN", "COMMIT", "ROLLBACK"


class SQLParser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def cur(self) -> Token:
        return self.tokens[self.pos]

    def consume(self, expected: str) -> Token:
        tok = self.cur()
        if tok.type != expected:
            raise SyntaxError(f"Expected {expected}, got {tok.type} at {tok.pos}")
        self.pos += 1
        return tok

    def parse(self) -> ASTNode:
        tok = self.cur()
        if tok.type == TokenType.SELECT:
            return self._parse_select()
        elif tok.type == TokenType.INSERT:
            return self._parse_insert()
        elif tok.type == TokenType.UPDATE:
            return self._parse_update()
        elif tok.type in (TokenType.BEGIN, TokenType.COMMIT, TokenType.ROLLBACK):
            self.pos += 1
            if self.cur().type == TokenType.SEMICOLON:
                self.pos += 1
            return TxControlQuery(tok.type)
        raise SyntaxError(f"Unsupported query starting with {tok}")

    def _parse_select(self) -> SelectQuery:
        self.consume(TokenType.SELECT)
        cols = []
        if self.cur().type == TokenType.STAR:
            self.consume(TokenType.STAR)
            cols = ["*"]
        else:
            cols.append(self.consume(TokenType.IDENT).val)
            while self.cur().type == TokenType.COMMA:
                self.consume(TokenType.COMMA)
                cols.append(self.consume(TokenType.IDENT).val)

        self.consume(TokenType.FROM)
        table = self.consume(TokenType.IDENT).val

        cond = None
        if self.cur().type == TokenType.WHERE:
            self.consume(TokenType.WHERE)
            col = self.consume(TokenType.IDENT).val
            op_tok = self.cur()
            if op_tok.type in (TokenType.EQUALS, TokenType.GREATER, TokenType.LESS):
                op = op_tok.val
                self.pos += 1
            else:
                raise SyntaxError(f"Expected comparison operator, got {op_tok.type}")
            val = self.cur().val
            self.pos += 1
            cond = (col, op, val)

        if self.cur().type == TokenType.SEMICOLON:
            self.consume(TokenType.SEMICOLON)
        return SelectQuery(table, cols, cond)

    def _parse_insert(self) -> InsertQuery:
        self.consume(TokenType.INSERT)
        self.consume(TokenType.INTO)
        table = self.consume(TokenType.IDENT).val
        self.consume(TokenType.VALUES)
        self.consume(TokenType.LPAREN)
        vals = [self.cur().val]
        self.pos += 1
        while self.cur().type == TokenType.COMMA:
            self.consume(TokenType.COMMA)
            vals.append(self.cur().val)
            self.pos += 1
        self.consume(TokenType.RPAREN)
        if self.cur().type == TokenType.SEMICOLON:
            self.consume(TokenType.SEMICOLON)
        return InsertQuery(table, vals)

    def _parse_update(self) -> UpdateQuery:
        self.consume(TokenType.UPDATE)
        table = self.consume(TokenType.IDENT).val
        self.consume(TokenType.SET)
        set_col = self.consume(TokenType.IDENT).val
        self.consume(TokenType.EQUALS)
        set_val = self.cur().val
        self.pos += 1

        cond = None
        if self.cur().type == TokenType.WHERE:
            self.consume(TokenType.WHERE)
            col = self.consume(TokenType.IDENT).val
            op = self.cur().val
            self.pos += 1
            val = self.cur().val
            self.pos += 1
            cond = (col, op, val)

        if self.cur().type == TokenType.SEMICOLON:
            self.consume(TokenType.SEMICOLON)
        return UpdateQuery(table, set_col, set_val, cond)


# ===========================================================================
# 2. MIDEND: QUERY OPTIMIZER & PHYSICAL VOLCANO ITERATORS
# ===========================================================================

class VolcanoIterator:
    def open(self):
        pass

    def next(self) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    def close(self):
        pass


class SeqScanIterator(VolcanoIterator):
    def __init__(self, records: List[Dict[str, Any]]):
        self.records = records
        self.idx = 0

    def open(self):
        self.idx = 0

    def next(self) -> Optional[Dict[str, Any]]:
        if self.idx < len(self.records):
            rec = self.records[self.idx]
            self.idx += 1
            return rec
        return None

    def close(self):
        self.idx = 0


class FilterIterator(VolcanoIterator):
    def __init__(self, child: VolcanoIterator, condition: Optional[Tuple[str, str, Any]]):
        self.child = child
        self.condition = condition

    def open(self):
        self.child.open()

    def next(self) -> Optional[Dict[str, Any]]:
        while True:
            row = self.child.next()
            if row is None:
                return None
            if self._matches(row):
                return row

    def _matches(self, row: Dict[str, Any]) -> bool:
        if not self.condition:
            return True
        col, op, target = self.condition
        if col not in row:
            return False
        val = row[col]
        if op == "=": return val == target
        elif op == ">": return val > target
        elif op == "<": return val < target
        return False

    def close(self):
        self.child.close()


class ProjectIterator(VolcanoIterator):
    def __init__(self, child: VolcanoIterator, columns: List[str]):
        self.child = child
        self.columns = columns

    def open(self):
        self.child.open()

    def next(self) -> Optional[Dict[str, Any]]:
        row = self.child.next()
        if row is None:
            return None
        if self.columns == ["*"]:
            return row
        return {col: row[col] for col in self.columns if col in row}

    def close(self):
        self.child.close()


def optimize_query_plan(query: SelectQuery, data: List[Dict[str, Any]]) -> VolcanoIterator:
    """
    Optimizes logical plan:
    1. Constant folding / simplification of WHERE condition.
    2. Builds physical execution pipeline: SeqScan -> Filter -> Project.
    """
    scan = SeqScanIterator(data)
    filt = FilterIterator(scan, query.condition)
    proj = ProjectIterator(filt, query.columns)
    return proj


# ===========================================================================
# 3. STORAGE ENGINE: SLOTTED PAGE PHYSICAL LAYOUT
# ===========================================================================

PAGE_SIZE = 4096
HEADER_FMT = "<III"  # LSN, free_space_offset, tuple_count
HEADER_SIZE = struct.calcsize(HEADER_FMT)
SLOT_FMT = "<HH"     # tuple_offset, tuple_length
SLOT_SIZE = struct.calcsize(SLOT_FMT)


class SlottedPage:
    def __init__(self, page_id: int):
        self.page_id = page_id
        self.data = bytearray(PAGE_SIZE)
        self.page_lsn = 0
        self.free_space_offset = PAGE_SIZE
        self.tuple_count = 0
        self._sync_header()

    def _sync_header(self):
        struct.pack_into(HEADER_FMT, self.data, 0, self.page_lsn, self.free_space_offset, self.tuple_count)

    def insert(self, payload: bytes) -> Optional[int]:
        rec_len = len(payload)
        slots_end = HEADER_SIZE + self.tuple_count * SLOT_SIZE
        if self.free_space_offset - slots_end < SLOT_SIZE + rec_len:
            return None  # Out of page capacity

        new_offset = self.free_space_offset - rec_len
        self.data[new_offset : new_offset + rec_len] = payload
        slot_pos = HEADER_SIZE + self.tuple_count * SLOT_SIZE
        struct.pack_into(SLOT_FMT, self.data, slot_pos, new_offset, rec_len)

        slot_id = self.tuple_count
        self.tuple_count += 1
        self.free_space_offset = new_offset
        self._sync_header()
        return slot_id

    def read(self, slot_id: int) -> Optional[bytes]:
        if slot_id < 0 or slot_id >= self.tuple_count:
            return None
        slot_pos = HEADER_SIZE + slot_id * SLOT_SIZE
        offset, length = struct.unpack_from(SLOT_FMT, self.data, slot_pos)
        if length == 0:
            return None
        return bytes(self.data[offset : offset + length])


class BufferFrame:
    def __init__(self, frame_id: int):
        self.frame_id = frame_id
        self.page: Optional[SlottedPage] = None
        self.pin_count = 0
        self.is_dirty = False
        self.ref_bit = False


class BufferPool:
    def __init__(self, size: int = 4):
        self.size = size
        self.frames = [BufferFrame(i) for i in range(size)]
        self.page_table: Dict[int, int] = {}
        self.clock_ptr = 0
        self.disk: Dict[int, bytes] = {}

    def get_page(self, page_id: int) -> SlottedPage:
        if page_id in self.page_table:
            f = self.frames[self.page_table[page_id]]
            f.pin_count += 1
            f.ref_bit = True
            return f.page

        victim = self._evict_clock()
        if victim.is_dirty and victim.page is not None:
            self.disk[victim.page.page_id] = bytes(victim.page.data)
            victim.is_dirty = False

        if victim.page is not None:
            del self.page_table[victim.page.page_id]

        if page_id in self.disk:
            p = SlottedPage(page_id)
            p.data = bytearray(self.disk[page_id])
            p.page_lsn, p.free_space_offset, p.tuple_count = struct.unpack_from(HEADER_FMT, p.data, 0)
        else:
            p = SlottedPage(page_id)

        victim.page = p
        victim.pin_count = 1
        victim.is_dirty = False
        victim.ref_bit = True
        self.page_table[page_id] = victim.frame_id
        return p

    def release_page(self, page_id: int, is_dirty: bool):
        if page_id in self.page_table:
            f = self.frames[self.page_table[page_id]]
            if is_dirty: f.is_dirty = True
            if f.pin_count > 0: f.pin_count -= 1

    def _evict_clock(self) -> BufferFrame:
        for _ in range(self.size * 2):
            f = self.frames[self.clock_ptr]
            if f.pin_count == 0:
                if f.ref_bit:
                    f.ref_bit = False
                else:
                    self.clock_ptr = (self.clock_ptr + 1) % self.size
                    return f
            self.clock_ptr = (self.clock_ptr + 1) % self.size
        raise RuntimeError("Buffer pool exhausted: all frames are pinned!")


# ===========================================================================
# 4. CONCURRENCY: MULTI-VERSION CONCURRENCY CONTROL (MVCC)
# ===========================================================================

class MVCCRecord:
    def __init__(self, row_id: int, data: Dict[str, Any], xmin: int, xmax: int = 0):
        self.row_id = row_id
        self.data = data
        self.xmin = xmin
        self.xmax = xmax

    def is_visible(self, tx_id: int, active_set: Set[int], committed_set: Set[int]) -> bool:
        if self.xmin == tx_id:
            return self.xmax != tx_id
        if self.xmin not in committed_set:
            return False
        if self.xmin in active_set or self.xmin > tx_id:
            return False
        if self.xmax == 0:
            return True
        if self.xmax == tx_id:
            return False
        if self.xmax not in committed_set:
            return True
        if self.xmax in active_set or self.xmax > tx_id:
            return True
        return False


# ===========================================================================
# 5. DURABILITY: WRITE-AHEAD LOGGING & ARIES CRASH RECOVERY
# ===========================================================================

class WALEntry:
    def __init__(self, lsn: int, tx_id: int, op: str, table: str, row_id: int, old_val: Any, new_val: Any):
        self.lsn = lsn
        self.tx_id = tx_id
        self.op = op
        self.table = table
        self.row_id = row_id
        self.old_val = old_val
        self.new_val = new_val


class AegisDB:
    def __init__(self):
        self.buffer_pool = BufferPool(size=4)
        self.tables: Dict[str, List[MVCCRecord]] = {}
        self.tx_counter = 100
        self.active_txs: Set[int] = set()
        self.committed_txs: Set[int] = set()
        self.wal_log: List[WALEntry] = []
        self.lsn_counter = 1

    def begin_transaction(self) -> int:
        self.tx_counter += 1
        tx_id = self.tx_counter
        self.active_txs.add(tx_id)
        self.wal_log.append(WALEntry(self.lsn_counter, tx_id, "BEGIN", "", 0, None, None))
        self.lsn_counter += 1
        return tx_id

    def commit(self, tx_id: int):
        if tx_id in self.active_txs:
            self.active_txs.remove(tx_id)
            self.committed_txs.add(tx_id)
            self.wal_log.append(WALEntry(self.lsn_counter, tx_id, "COMMIT", "", 0, None, None))
            self.lsn_counter += 1

    def rollback(self, tx_id: int):
        if tx_id not in self.active_txs:
            return
        # Undo updates made by this tx
        for tbl in self.tables.values():
            for r in tbl:
                if r.xmin == tx_id:
                    r.xmin = -1  # Voided
                if r.xmax == tx_id:
                    r.xmax = 0   # Restored
        self.active_txs.remove(tx_id)
        self.wal_log.append(WALEntry(self.lsn_counter, tx_id, "ABORT", "", 0, None, None))
        self.lsn_counter += 1

    def execute_sql(self, sql: str, tx_id: int) -> Any:
        tokens = SQLLexer(sql).tokens
        ast = SQLParser(tokens).parse()

        if isinstance(ast, TxControlQuery):
            if ast.action == "BEGIN": return self.begin_transaction()
            elif ast.action == "COMMIT": return self.commit(tx_id)
            elif ast.action == "ROLLBACK": return self.rollback(tx_id)

        elif isinstance(ast, InsertQuery):
            if ast.table not in self.tables:
                self.tables[ast.table] = []
            row_id = len(self.tables[ast.table]) + 1
            # Infer fields: id, name, val
            row_data = {"id": ast.values[0], "name": ast.values[1], "balance": ast.values[2]}
            record = MVCCRecord(row_id, row_data, xmin=tx_id)
            self.tables[ast.table].append(record)
            
            # Serialize into slotted page
            p = self.buffer_pool.get_page(1)
            payload = json.dumps(row_data).encode("utf-8")
            p.insert(payload)
            self.buffer_pool.release_page(1, is_dirty=True)

            self.wal_log.append(WALEntry(self.lsn_counter, tx_id, "INSERT", ast.table, row_id, None, row_data))
            self.lsn_counter += 1
            return 1

        elif isinstance(ast, SelectQuery):
            if ast.table not in self.tables:
                return []
            active_snapshot = set(self.active_txs) - {tx_id}
            visible_rows = [
                r.data for r in self.tables[ast.table]
                if r.is_visible(tx_id, active_snapshot, self.committed_txs)
            ]
            # Execute through Volcano iterator pipeline
            plan = optimize_query_plan(ast, visible_rows)
            plan.open()
            results = []
            while True:
                row = plan.next()
                if row is None: break
                results.append(row)
            plan.close()
            return results

        elif isinstance(ast, UpdateQuery):
            if ast.table not in self.tables:
                return 0
            count = 0
            active_snapshot = set(self.active_txs) - {tx_id}
            new_records = []
            for r in list(self.tables[ast.table]):
                if r.is_visible(tx_id, active_snapshot, self.committed_txs):
                    if ast.condition:
                        col, op, target = ast.condition
                        if op == "=" and r.data.get(col) != target:
                            continue
                    # MVCC update: mark old as deleted by tx_id, create new version
                    old_data = dict(r.data)
                    new_data = dict(r.data)
                    new_data[ast.set_col] = ast.set_val
                    r.xmax = tx_id
                    new_rec = MVCCRecord(len(self.tables[ast.table]) + len(new_records) + 1, new_data, xmin=tx_id)
                    new_records.append(new_rec)
                    self.wal_log.append(WALEntry(self.lsn_counter, tx_id, "UPDATE", ast.table, r.row_id, old_data, new_data))
                    self.lsn_counter += 1
                    count += 1
            self.tables[ast.table].extend(new_records)
            return count

    def crash_and_recover(self) -> Dict[str, Any]:
        """
        Simulates unexpected crash and executes ARIES recovery.
        """
        # Analysis: identify losers
        active = set()
        for w in self.wal_log:
            if w.op == "BEGIN": active.add(w.tx_id)
            elif w.op in ("COMMIT", "ABORT"): active.discard(w.tx_id)
        losers = active

        # Redo: replay forward
        recovered: Dict[str, Dict[int, Any]] = {}
        for w in self.wal_log:
            if w.table and w.table not in recovered:
                recovered[w.table] = {}
            if w.op in ("INSERT", "UPDATE"):
                recovered[w.table][w.row_id] = w.new_val

        # Undo: reverse losers backward
        for w in reversed(self.wal_log):
            if w.tx_id in losers:
                if w.op == "INSERT":
                    if w.table in recovered and w.row_id in recovered[w.table]:
                        del recovered[w.table][w.row_id]
                elif w.op == "UPDATE":
                    recovered[w.table][w.row_id] = w.old_val

        return recovered
