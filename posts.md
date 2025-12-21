---
layout: list
title: Posts
description: >
  Posts, trying to be informative if not always exact.
grouped: true
---

<ul>
  {% for post in site.posts %}
    {% unless posts.categories contains 'writing' %}
      <li>
        <a href="{{ post.url }}">{{ post.title }}</a>
      </li>
    {% endunless %}
  {% endfor %}
</ul>
