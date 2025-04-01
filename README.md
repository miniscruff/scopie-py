# Scopie-py

[![PyPI - Version](https://img.shields.io/pypi/v/scopie?style=for-the-badge)](https://pypi.org/project/scopie/)
[![Static Badge](https://img.shields.io/badge/Stable-black?style=for-the-badge&logo=readthedocs&label=Docs)](https://scopie-py.readthedocs.io/en/stable/)

Python implementation of [scopie](https://github.com/miniscruff/scopie).

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
