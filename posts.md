---
layout: list
title: Posts
description: >
  Posts, trying to be informative if not always correct.
grouped: true
---

<ul>
  {% for post in site.posts %}
    <li>
      <a href="{{ post.url }}">{{ post.title }}</a>
    </li>
  {% endfor %}
</ul>
