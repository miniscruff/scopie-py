# scopie-py
Python implementation of scopie

```python
from scopie import is_allowed

users = {
    "elsa": {
        "rules": ["allow/blog/create|update"],
    },
    "bella": {
        "rules": ["allow/blog/create"],
    },
}

blogPosts = {}

def create_blog(username, blogSlug, blogContent):
    user = users[username]
    if is_allowed(["blog/create"], user["rules"]):
        blogPosts[blogSlug] = {
            "author": user,
            "content": blogContent,
        }

def update_blog(username, blogSlug, blogContent):
    user = users[username]
    if is_allowed(["blog/update"], user["rules"]):
        blogPosts[blogSlug] = {
            "author": user,
            "content": blogContent,
        }
```
