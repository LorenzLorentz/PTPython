import json
from app.plagiarism.build_pdg import PDGBuilder
from app.plagiarism.calc_sim import GraphSimilarity

def gene_report(pdg1:dict, pdg2:dict, sim_res:dict) -> str:
    node_mapping = sim_res['node_mapping']
    reverse_node_mapping = {v: k for k, v in node_mapping.items()}
    
    vis_nodes = []
    vis_edges = []
    
    # 处理节点
    for node in pdg1['nodes']:
        status = "common" if node['id'] in node_mapping else "unique_p1"
        vis_nodes.append({
            "id": f"p1_{node['id']}",
            "original_id": node['id'],
            "source_program": "p1",
            "status": status,
            "label": node['label']
        })

    for node in pdg2['nodes']:
        if node['id'] not in reverse_node_mapping:
            vis_nodes.append({
                "id": f"p2_{node['id']}",
                "original_id": node['id'],
                "source_program": "p2",
                "status": "unique_p2",
                "label": node['label']
            })

    # 处理边
    matched_p1_edges = {(e['p1_edge']['source'], e['p1_edge']['target'], e['p1_edge']['type']) for e in sim_res['matched_edges']}
    matched_p2_edges = {(e['p2_edge']['source'], e['p2_edge']['target'], e['p2_edge']['type']) for e in sim_res['matched_edges']}

    for edge in pdg1['edges']:
        src, tgt, etype = edge['source'], edge['target'], edge['type']
        status = "common" if (src, tgt, etype) in matched_p1_edges else "unique_p1"
        vis_edges.append({
            "source": f"p1_{src}",
            "target": f"p1_{tgt}",
            "type": etype,
            "status": status
        })

    for edge in pdg2['edges']:
        src, tgt, etype = edge['source'], edge['target'], edge['type']
        if (src, tgt, etype) not in matched_p2_edges:
             vis_edges.append({
                "source": f"p2_{src}",
                "target": f"p2_{tgt}",
                "type": etype,
                "status": "unique_p2"
            })
            
    report = {
        "sim_scores": {
            "sim_score": sim_res['sim_score'],
            "node_score": sim_res['node_score'],
            "edge_score": sim_res['edge_score']
        },
        "mappings": {
            "node_mapping_p1_to_p2": sim_res['node_mapping'],
            "matched_edges": sim_res['matched_edges']
        },
        "visualization_summary": {
            "nodes": vis_nodes,
            "edges": vis_edges
        }
    }
    
    return json.dumps(report, indent=2)

def get_report(pdg1:dict, pdg2:dict) -> str:
    hashes1 = pdg1.pop("hashed_nodes")
    hashes2 = pdg2.pop("hashed_nodes")

    similarity_results = GraphSimilarity(pdg1, pdg2, hashes1, hashes2).calculate_similarity()

    return gene_report(pdg1, pdg2, similarity_results)
