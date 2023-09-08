from neomodel import StructuredNode, StringProperty, StructuredRel, IntegerProperty, RelationshipTo, DateProperty, cardinality
from typing import List
from loguru import logger
import openai
import tiktoken
from .neo4vec import FloatVectorProperty

class ContentSection(StructuredRel):
    index = IntegerProperty(required=True)

class Content(StructuredNode):
    content = StringProperty(required=True)
    embedding = FloatVectorProperty(length=1536)
    published_at = DateProperty()

    def before_save(self):
        response = openai.Embedding.create(model="text-embedding-ada-002", input=self.content)
        self.embedding = response['data'][0]['embedding']


class TrainingExample(Content):
    pass


class Section(Content):
    pass

class SourceInterview(StructuredNode):
    title = StringProperty(unique_index=True)
    training_examples = RelationshipTo('TrainingExample', 'HAS_TRAINING_EXAMPLE', cardinality=cardinality.OneOrMore)

    def add_section(self, content: str, index: int):
        section = Section(content, index).save()
        self.sections.connect(section)

class Blog(StructuredNode):
    title = StringProperty(unique_index=True)
    base_url = StringProperty(unique_index=True)
    posts = RelationshipTo('BlogPost', 'HAS_POST', cardinality=cardinality.OneOrMore)


class BlogPost(StructuredNode):
    title = StringProperty(unique_index=True)
    author = StringProperty()
    sections = RelationshipTo('Section', 'HAS_SECTION', cardinality=cardinality.OneOrMore, model=ContentSection)
    full_text = StringProperty()

    def post_save(self):
        tokenizer = tiktoken.get_encoding("cl100k_base")
        paragraphs = self.full_text.split('\n')
        current_content = ''
        sections = []
        logger.info(f"Splitting {self.title} into sections")
        for index, paragraph in enumerate(paragraphs):
            tokens = list(tokenizer.encode(paragraph))
            if len(tokens) > 4096:
                sections.push(current_content)
                current_content = ''
            else:
                current_content += paragraph
        if current_content:
            sections.append(current_content)
        for index, section in enumerate(sections):
            section = Section(content=section).save()
            self.sections.connect(section, {"index": index})
            logger.success(f"Split {self.title} into {len(sections)} sections")
        logger.success(f"Saved {self.title} to database")
    @staticmethod
    def _split_paragraph(tokens: List[str]) -> List[List[str]]:
        return [tokens[i:i + 4096] for i in range(0, len(tokens), 4096)]
