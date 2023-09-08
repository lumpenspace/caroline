from neomodel import StructuredNode, StringProperty, IntegerProperty, RelationshipTo, DateProperty, cardinality
from typing import List
from loguru import logger
import tiktoken
from .neo4vec import  ContentMixin, SimilarityRel, ContentSection, get_embedding

class TrainingExample(StructuredNode, ContentMixin):
    pass

class Section(StructuredNode, ContentMixin):
    index_name = "blog_post_sections"

class Exchange(StructuredNode):
    question = StringProperty(required=True)
    answer = StringProperty(required=True)
    content = StringProperty(required=True)
    similar_sections = RelationshipTo('Section', 'HAS_SIMILAR_SECTION', cardinality=cardinality.OneOrMore, model=SimilarityRel)

    def pre_save(self):
        self.content = f"Q: {self.question.strip()}\n\nA: {self.answer.strip()}"

    def post_create(self):
        logger.info(f"Creating exchange for question: {self.question}")
        similar = Section.get_similar(f"Q: {self.question}\n\nA: {self.answer}")
        for section in similar:
            print(section)

class SourceInterview(StructuredNode):
    title = StringProperty(unique_index=True)
    url = StringProperty(unique_index=True)

    exchanges = RelationshipTo('Exchange', 'HAS_EXCHANGE', cardinality=cardinality.OneOrMore)

    def add_exchanges(self, exchanges: List[Exchange]):
        for exchange in exchanges:
            embedding = get_embedding(f"Q: {exchange.question}\n\nA: {exchange.answer}")
            similar = Section.get_similar(embedding)
            print(similar)
        

class Blog(StructuredNode):
    title = StringProperty(unique_index=True)
    base_url = StringProperty(unique_index=True)
    posts = RelationshipTo('BlogPost', 'HAS_POST', cardinality=cardinality.ZeroOrMore)


class BlogPost(StructuredNode):
    title = StringProperty(unique_index=True)
    author = StringProperty()
    sections = RelationshipTo('Section', 'HAS_SECTION', cardinality=cardinality.ZeroOrMore, model=ContentSection)
    full_text = StringProperty()
    url = StringProperty(unique_index=True)

    def post_save(self):
        if (self.sections.all()):
            print("Sections already exist for this blog post")
            return
        tokenizer = tiktoken.get_encoding("cl100k_base")
        paragraphs = self.full_text.split('\n')
        section = ""
        sections = []
        for index, paragraph in enumerate(paragraphs):
            tokens = list(tokenizer.encode(section + paragraph))
            if len(tokens) > 4096:
                sections.append(section)
                section = paragraph
            else:
                section += paragraph
            if index == len(paragraphs) - 1:
                sections.append(section)
        for index, section in enumerate(sections):
            section = Section(content=section).save()
            self.sections.connect(section, {'index': index})
            logger.info(f"Created section {index} for blog post {self.title}")

    @staticmethod
    def _split_paragraph(tokens: List[str]) -> List[List[str]]:
        return [tokens[i:i + 4096] for i in range(0, len(tokens), 4096)]