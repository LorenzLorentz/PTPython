import ast
from collections import defaultdict

from app.plagiarism.build_cfg import CFGBuilder, BasicBlock
from app.plagiarism.get_cano_hash import get_cano_hash

class PDGBuilder:
    """PDG构建器基类"""
    def __init__(self, code: str):
        self.code = code
        self.pdg = {"nodes": [], "edges": [], "hashed_nodes": {}}
        # self.cfg = None

    def build(self):
        # 1. Code -> AST
        ast_tree = ast.parse(self.code)

        # 2. AST -> CFG
        cfg_builder = CFGBuilder()
        cfg = cfg_builder.build(ast_tree)
        # self.cfg = cfg
        self._create_nodes(cfg)
        self._add_hashed_nodes(cfg)

        # 3. CFG -> PDG
        # 控制依赖
        control_deps = self._ctrl_dep(cfg)
        self._add_edges(control_deps, "control")

        # 数据依赖
        data_deps = self._data_dep(cfg)
        self._add_edges(data_deps, "data")
        
        return self.pdg
    
    def _add_hashed_nodes(self, cfg):
        for block_id, block in cfg['blocks'].items():
            self.pdg['hashed_nodes'][block_id] = get_cano_hash(block.statements)

    def _create_nodes(self, cfg):
        for block_id, block in cfg['blocks'].items():
            self.pdg['nodes'].append({
                "id": block_id,
                "label": block.get_label(),
                "type": "block"
            })

    def _add_edges(self, deps, dep_type):
        for source, target in deps:
            self.pdg['edges'].append({
                "source": source,
                "target": target,
                "type": dep_type
            })

    def _ctrl_dep(self, cfg):
        """计算控制依赖。"""
        deps = []
        post_doms = self._get_post_dom(cfg)
        
        for block_id, block in cfg['blocks'].items():
            if len(block.successors) > 1:
                for succ in block.successors:
                    q = [succ]
                    visited = {succ}
                    while q:
                        curr = q.pop(0)
                        
                        if block_id not in post_doms[curr.id]:
                             deps.append((block_id, curr.id))

                        for child in curr.successors:
                            if child not in visited:
                                visited.add(child)
                                q.append(child)
        return list(set(deps)) # 去重

    def _get_post_dom(self, cfg):
        """获取后支配者"""
        exit_id = cfg['exit'].id
        nodes = list(cfg['blocks'].keys())
        post_doms = {n: set(nodes) for n in nodes}
        post_doms[exit_id] = {exit_id}

        changed = True
        while changed:
            changed = False
            for n_id in nodes:
                if n_id == exit_id: continue
                
                # Preds in reversed graph are successors in original graph
                preds = [p.id for p in cfg['blocks'][n_id].successors]
                if not preds: continue

                new_doms = set.intersection(*(post_doms[p_id] for p_id in preds))
                new_doms.add(n_id)
                
                if new_doms != post_doms[n_id]:
                    post_doms[n_id] = new_doms
                    changed = True
        return post_doms

    def _data_dep(self, cfg):
        """计算数据依赖"""
        # 查找定义和使用
        defs, uses = {}, {}
        for block_id, block in cfg['blocks'].items():
            block_defs, block_uses = self._get_defs_uses(block)
            defs[block_id] = block_defs
            uses[block_id] = block_uses
        
        # 到达-定义分析
        reaching_defs = self._run_reaching_def(cfg, defs)

        # 创建数据依赖边
        deps = []
        for block_id, block_uses in uses.items():
            for var_name in block_uses:
                if block_id in reaching_defs:
                    for def_block_id, defined_var in reaching_defs[block_id]:
                        if var_name == defined_var:
                            deps.append((def_block_id, block_id))
        return list(set(deps))
    
    def _get_defs_uses(self, block:BasicBlock):
        """查找定义和使用"""
        defs, uses = set(), set()
        for stmt in block.statements:
            for node in ast.walk(stmt):
                if isinstance(node, ast.Name):
                    if isinstance(node.ctx, ast.Store):
                        defs.add(node.id)
                    elif isinstance(node.ctx, ast.Load):
                        uses.add(node.id)
        return defs, uses
    
    def _run_reaching_def(self, cfg, defs):
        in_sets = defaultdict(set)
        out_sets = defaultdict(set)
        
        all_blocks = list(cfg['blocks'].values())
        
        changed = True
        while changed:
            changed = False
            for block in all_blocks:
                in_sets[block.id] = set().union(*(out_sets[p.id] for p in block.predecessors))

                gen = {(block.id, var) for var in defs[block.id]}

                kill = set()
                for d_block, d_var in in_sets[block.id]:
                    if d_var in defs[block.id]:
                        kill.add((d_block, d_var))
                        
                new_out = gen.union(in_sets[block.id] - kill)
                
                if new_out != out_sets[block.id]:
                    out_sets[block.id] = new_out
                    changed = True
                    
        return in_sets