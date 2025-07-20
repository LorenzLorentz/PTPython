import ast

class BasicBlock:
    """CFG中的基本块"""
    def __init__(self, block_id):
        self.id = block_id
        self.statements = [] # 块内的语句列表
        self.predecessors = [] # 前驱块列表
        self.successors = [] # 后继块列表

    def __repr__(self):
        return f"Block-{self.id}"

    def get_label(self):
        """可视化"""
        if not self.statements:
            return f"Block-{self.id} (empty)"

        lines = [ast.unparse(s) for s in self.statements[:3]]
        if len(self.statements) > 3:
            lines.append("...")
        return f"Block-{self.id}\n" + "\n".join(lines)

class CFGBuilder(ast.NodeVisitor):
    """利用AST构建CFG"""
    def __init__(self):
        self.current_block:BasicBlock = None
        self.next_block_id = 0
        
        self.blocks = {}
        self.entry_node:BasicBlock = None # 入口节点
        self.exit_node = self._new_block() # 出口节点

    def _new_block(self) -> BasicBlock:
        block_id = self.next_block_id
        self.next_block_id += 1
        self.blocks[block_id] = BasicBlock(block_id)
        return self.blocks[block_id]

    def _add_edge(self, from_block:BasicBlock, to_block:BasicBlock):
        if to_block not in from_block.successors:
            from_block.successors.append(to_block)
        if from_block not in to_block.predecessors:
            to_block.predecessors.append(from_block)

    def build(self, ast_tree) -> dict:
        """构建CFG"""
        self.entry_node = self._new_block()
        self.current_block = self.entry_node
        self.visit(ast_tree)
        # 将最后一个块连接到出口
        if self.current_block and self.current_block != self.exit_node:
             self._add_edge(self.current_block, self.exit_node)
        self.cfg = {"entry": self.entry_node, "exit": self.exit_node, "blocks": self.blocks}
        return self.cfg

    def visit(self, node):
        if self.current_block is None:
            self.current_block = self._new_block()
        super().visit(node)

    def _visit_statements(self, statements):
        for stmt in statements:
            self.visit(stmt)

    def visit_If(self, node:ast.If):
        # 1. 当前块包含if条件
        if_block = self.current_block
        if_block.statements.append(node.test)

        # 2. 创建then和else分支的块
        then_block = self._new_block()
        self._add_edge(if_block, then_block)
        
        # 3. 访问then分支
        self.current_block = then_block
        self._visit_statements(node.body)
        then_end_block = self.current_block

        # 4. 访问else分支
        if node.orelse:
            else_block = self._new_block()
            self._add_edge(if_block, else_block)
            self.current_block = else_block
            self._visit_statements(node.orelse)
            else_end_block = self.current_block
        else:
            else_end_block = if_block # 直接从if跳到合并点

        # 5. 创建合并块
        merge_block = self._new_block()
        self._add_edge(then_end_block, merge_block)
        self._add_edge(else_end_block, merge_block)
        
        self.current_block = merge_block
        
    def visit_For(self, node:ast.For):
        # 1. 循环头
        header_block = self._new_block()
        self._add_edge(self.current_block, header_block)
        header_block.statements.append(node.iter)
        header_block.statements.append(node.target)

        # 2. 循环体
        body_block = self._new_block()
        self._add_edge(header_block, body_block)
        
        # 3. 循环结束
        after_loop_block = self._new_block()
        self._add_edge(header_block, after_loop_block)

        # 4. 访问循环体
        self.current_block = body_block
        self._visit_statements(node.body)
        self._add_edge(self.current_block, header_block)

        self.current_block = after_loop_block
    
    def visit_While(self, node:ast.While):
        # 1. 循环头
        header_block = self._new_block()
        self._add_edge(self.current_block, header_block)
        header_block.statements.append(node.test)

        # 2. 循环体
        body_block = self._new_block()
        self._add_edge(header_block, body_block)
        
        # 3. 循环结束
        after_loop_block = self._new_block()
        self._add_edge(header_block, after_loop_block)

        # 4. 访问循环体
        self.current_block = body_block
        self._visit_statements(node.body)
        self._add_edge(self.current_block, header_block)

        self.current_block = after_loop_block

    def generic_visit(self, node):
        """对于非控制流语句, 直接添加到当前块"""
        if isinstance(node, ast.stmt):
            if self.current_block is None:
                self.current_block = self._new_block()
            self.current_block.statements.append(node)
        super().generic_visit(node)