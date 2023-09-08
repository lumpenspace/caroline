from feedparser import parse, FeedParserDict
from .models import Blog, BlogPost
from loguru import logger
import requests
from .blog_content_selectors import post_content_selectors
from bs4 import BeautifulSoup

def ingest_blog(rss_url:str, author_name:str, base_url:str):
    feed:FeedParserDict = parse(rss_url)
    if (blog := Blog.nodes.get_or_none(title=feed.feed.title)) is not None:
        logger.info(f"Blog {blog.title} already exists in database")
    else:
        logger.info(f"Creating blog {feed.feed.title} in database")
        blog = Blog(title=feed.feed.title, base_url=base_url)
    blog.save()
    logger.info(f"Saving {blog.title} to database")

    for entry in feed.entries:
        logger.info(f"Saving {entry.title} to {blog.title}")
        response = requests.get(entry.link)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Assuming the blog post content is in a <div> with class "post-content"
        selector = post_content_selectors[base_url]
        logger.info(f"Finding {selector} in {entry.link}")
        elements = soup.select(selector)
        if elements:
            full_text = elements[0].text
        else:
            logger.warning(f"No {selector} found in {entry.link}")
            continue
        blog_post = BlogPost.nodes.get_or_none(title=entry.title)
        if blog_post is None:
            blog_post = BlogPost(title=entry.title)
        blog_post.author = author_name
        blog_post.url = entry.link
        blog_post.full_text = full_text
        blog_post.save()        
    logger.success(f"Saved {blog.title} to database")

def ingest_paulgraham_blog():
    ingest_blog("http://www.aaronsw.com/2002/feeds/pgessays.rss", "Paul Graham", "paulgraham.com")