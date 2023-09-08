from feedparser import parse, FeedParserDict
from .models import Blog, BlogPost
from loguru import logger
import requests
from .content_selectors import post_content_selectors
from bs4 import BeautifulSoup

def ingest_blog(rss_url:str, author_name:str, base_url:str):
    feed:FeedParserDict = parse(rss_url)
    blogs = Blog.create_or_update({"title": feed.feed.title, "base_url": base_url})
    blog = blogs[0]
    blog.save()
    logger.info(f"Saving {blog.title} to database")
    for entry in feed.entries:
        if blog.posts.filter(title=entry.title):
            logger.info(f"Skipping {entry.title} because it already exists")
            continue
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
        blog_post = BlogPost(title=entry.title, author=author_name, full_text=full_text)
        blog_post.save()
        blog_post.post_save()
        blog.posts.connect(blog_post)
        logger.success(f"Saved {entry.title}")
    logger.success(f"Saved {blog.title} to database")


ingest_blog("http://www.aaronsw.com/2002/feeds/pgessays.rss", "Paul Graham", "paulgraham.com")