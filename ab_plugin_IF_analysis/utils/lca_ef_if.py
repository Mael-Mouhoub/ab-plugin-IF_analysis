from brightway2 import *
import pandas as pd
import ast 
import numpy as np

def lca_if(key,method_flows):
    #recupere la methode IF
    #fais un calcul de supply chain
    #identifie les activites necessaires
    #retourne un tableau
    random_method = list(methods)[1]
    method = Method(random_method)#random method we only need supply chain
    lca = LCA({key: 1}, random_method)
    lca.lci()
    lca.lcia()
    lca_score = lca.score
    activity_dict = lca.activity_dict
    supply_array = lca.supply_array
        
    results_df = pd.DataFrame(columns=["type",'product',"inventory","cf", 'activity', "crm", "content","content_scaled", "cf_unitaire" ,'lca_score'])
    for if_flow in method_flows:
        key_flow = ast.literal_eval(if_flow["key"])
        if key_flow in activity_dict :
            results_df.loc[len(results_df)] = {
            "type" : "IF",
            'product': if_flow["product"],
            'activity': Database(key_flow[0]).get(key_flow[1])["name"],
            "inventory":supply_array[activity_dict[key_flow]],
            "cf":if_flow["cf"],
            "crm":if_flow["crm"],
            'lca_score': if_flow["cf"] * supply_array[activity_dict[key_flow]],
            "content" : if_flow["content"], 
            "content_scaled" : if_flow["content"]*supply_array[activity_dict[key_flow]], 
            "cf_unitaire": if_flow["cf_unitaire"],
            }
    
    # Extraire les noms des colonnes et les données
    return(results_df)

# def lca_ef(key,method):
#     # 2. Créer et lancer l'analyse de cycle de vie
#     lca = LCA({key: 1}, method)
#     lca.lci(factorize=False)
#     lca.lcia()

#     # 3. Obtenir le vecteur d'inventaire total (B × x)
#     # (somme des colonnes de la matrice inventory → vecteur 2174 x 1)
#     inventory_vector = lca.inventory.sum(axis=1)
#     inventory_array = np.array(inventory_vector).flatten()  # Convertit en array 1D

#     # 4. Obtenir les flux élémentaires et leurs quantités
#     # flux élémentaires : correspondance entre les lignes de l'inventaire et les flux biosphère
#     biosphere_dict = lca.biosphere_dict
#     reverse_biosphere_dict = {v: k for k, v in biosphere_dict.items()}

#     elementary_flows = []

#     for i, amount in enumerate(inventory_array):
#         flow_index = reverse_biosphere_dict.get(i)
#         if flow_index:
#             product = get_activity(flow_index)
#             elementary_flows.append((product['name'], product['unit'], amount))

#     cf_by_flows = []
#     flow_index = 0

#     for elementary_flow in elementary_flows:
#         cf = lca.characterization_matrix[flow_index, flow_index] if flow_index < lca.characterization_matrix.shape[0] else 0
#         partial_score = elementary_flow[2] * cf
#         #print(f"{elementary_flow[0]}: {partial_score} {elementary_flow[1]}")
#         cf_by_flows.append((elementary_flow[0],elementary_flow[2],cf,partial_score,elementary_flow[1]))
#         flow_index=flow_index+1
#     cf_by_flows_sorted = sorted(cf_by_flows, key=lambda x: x[3] == 0)

#     results_df = pd.DataFrame(columns=["type",'product',"inventory","cf", 'activity', "crm", 'lca_score'])
#     for ef_flow in cf_by_flows_sorted:
#         results_df.loc[len(results_df)] = {
#         "type" : "EF",
#         'product': ef_flow[0],
#         'activity': "",
#         "inventory":ef_flow[1],
#         "cf":ef_flow[2],
#         "crm" : ef_flow["crm"],
#         'lca_score': ef_flow[3],
#         }
#     # Extraire les noms des colonnes et les données
#     return(results_df)

