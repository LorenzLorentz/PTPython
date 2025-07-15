import numpy as np

class GraphSimilarity:
    """计算PDG的相似度。"""
    def __init__(self, pdg1:dict, pdg2:dict, node_hashes1:dict, node_hashes2:dict):
        self.pdg1 = pdg1
        self.pdg2 = pdg2
        self.nodes1 = self.pdg1['nodes']
        self.nodes2 = self.pdg2['nodes']
        self.edges1 = self.pdg1['edges']
        self.edges2 = self.pdg2['edges']
        self.node_hashes1 = node_hashes1
        self.node_hashes2 = node_hashes2

    def _calc_node_sim(self) -> np.ndarray:
        """计算节点相似度矩阵"""
        num_nodes1 = len(self.nodes1)
        num_nodes2 = len(self.nodes2)
        sim_matrix = np.zeros((num_nodes1, num_nodes2))

        for i in range(num_nodes1):
            for j in range(num_nodes2):
                node1_id = self.nodes1[i]['id']
                node2_id = self.nodes2[j]['id']
                if self.node_hashes1.get(node1_id) == self.node_hashes2.get(node2_id) and self.node_hashes1.get(node1_id) != "":
                    sim_matrix[i, j] = 1.0
        return sim_matrix

    def _get_node_mapping(self, sim_matrix: np.ndarray) -> dict:
        """寻找节点映射"""
        mapping = {}

        sim_matrix_copy = sim_matrix.copy()
        while np.max(sim_matrix_copy) > 0:
            i, j = np.unravel_index(np.argmax(sim_matrix_copy), sim_matrix_copy.shape)
            
            p1_node_id = self.nodes1[i]['id']
            p2_node_id = self.nodes2[j]['id']
            
            mapping[p1_node_id] = p2_node_id

            sim_matrix_copy[i, :] = 0
            sim_matrix_copy[:, j] = 0
            
        return mapping

    def calculate_similarity(self) -> dict:
        """计算相似度"""
        sim_matrix = self._calc_node_sim()
        node_mapping = self._get_node_mapping(sim_matrix)

        # 计算节点匹配分数
        matched_nodes_count = len(node_mapping)
        total_nodes = len(self.nodes1) + len(self.nodes2)
        node_score = (2 * matched_nodes_count) / total_nodes if total_nodes > 0 else 0

        # 计算边匹配分数
        p2_edge_set = {(e['source'], e['target'], e['type']) for e in self.edges2}
        matched_edges_count = 0
        matched_edges_details = []

        for edge1 in self.edges1:
            p1_src, p1_tgt = edge1['source'], edge1['target']
            
            # 检查边的源和目标节点是否都在映射中
            if p1_src in node_mapping and p1_tgt in node_mapping:
                p2_src = node_mapping[p1_src]
                p2_tgt = node_mapping[p1_tgt]
                
                # 检查是否存在类型和端点都匹配的边
                if (p2_src, p2_tgt, edge1['type']) in p2_edge_set:
                    matched_edges_count += 1
                    matched_edges_details.append({
                        "p1_edge": edge1,
                        "p2_edge": {'source': p2_src, 'target': p2_tgt, 'type': edge1['type']}
                    })

        total_edges = len(self.edges1) + len(self.edges2)
        edge_score = (2 * matched_edges_count) / total_edges if total_edges > 0 else 0

        # 计算综合分数
        sim = 0.4*node_score + 0.6*edge_score

        return {
            "sim_score": sim,
            "node_score": node_score,
            "edge_score": edge_score,
            "node_mapping": node_mapping,
            "matched_edges": matched_edges_details
        }