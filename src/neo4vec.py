import neomodel
from neomodel import db, Property, FloatProperty

def create_vector_index(index_name:str, label:str):
    query = neomodel.cypher_query(f"CALL db.index.vector.createNodeIndex('{index_name}', '{label}', 'embedding', 1536, 'cosine')")
    try:
        db.cypher_query(query)
    except Exception as e:
        print(f"Failed to execute query: {query}. Error: {e}")

class FloatVectorProperty(Property):
    def __init__(self, length, *args, **kwargs):
        self.length = length
        self.vector = [FloatProperty() for _ in range(length)]
        super().__init__(*args, **kwargs)

    def inflate(self, value):
        if len(value) != self.length:
            raise ValueError(f"Vector length must be {self.length}")
        return [prop.inflate(val) for prop, val in zip(self.vector, value)]

    def deflate(self, value):
        if len(value) != self.length:
            raise ValueError(f"Vector length must be {self.length}")
        return [prop.deflate(val) for prop, val in zip(self.vector, value)]