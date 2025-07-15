import ast
import hashlib

class AstCanonicalizer(ast.NodeTransformer):
    """规范化变量名和常量, 替换变量名和常量为占位符"""
    def __init__(self):
        self.var_map = {}
        self.const_map = {}
        self.var_count = 0
        self.const_count = 0

    def _get_var_name(self, original_name):
        if original_name not in self.var_map:
            self.var_map[original_name] = f"VAR_{self.var_count}"
            self.var_count += 1
        return self.var_map[original_name]

    def _get_const_name(self, original_val):
        if original_val not in self.const_map:
            self.const_map[original_val] = f"CONST_{self.const_count}"
            self.const_count += 1
        return self.const_map[original_val]

    def visit_Name(self, node: ast.Name):
        # 替换变量名
        node.id = self._get_var_name(node.id)
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # 替换函数名和参数名
        node.name = self._get_var_name(node.name)
        if node.args:
            for arg in node.args.args:
                arg.arg = self._get_var_name(arg.arg)
        self.generic_visit(node)
        return node
        
    def visit_Attribute(self, node: ast.Attribute):
        # 只访问value部分, 不改变attr名称
        self.visit(node.value)
        return node

    def visit_Constant(self, node: ast.Constant):
        # 替换常量值
        if type(node.value) in [int, float, str]:
            node.value = self._get_const_name(node.value)
        return node

def get_cano_hash(stmts: list[ast.stmt]) -> str:
    """计算AST语句的规范化内容哈希"""
    if not stmts:
        return ""
    
    # 规范化
    canonicalizer = AstCanonicalizer()
    canonical_stmts = [canonicalizer.visit(ast.fix_missing_locations(ast.parse(ast.unparse(s)))) for s in stmts]

    # 转换回字符串
    try:
        canonical_code = "\n".join([ast.unparse(s) for s in canonical_stmts])
    except Exception:
        canonical_code = str(ast.dump(ast.Module(body=canonical_stmts)))

    # 计算哈希
    return hashlib.sha256(canonical_code.encode('utf-8')).hexdigest()