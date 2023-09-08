from neomodel import  db

def create_vector_index(index_name:str, label:str):
    query = db.cypher_query(f"CALL db.index.vector.createNodeIndex('{index_name}', '{label}', 'embedding', 1536, 'cosine') return count(*)")
    try:
        db.cypher_query(query)
    except Exception as e:
        print(f"Failed to execute query: {query}. Error: {e}")

def create_vector_indices():
    create_vector_index("blog_post_sections", "Section")
    create_vector_index("exchanges", "Exchange")