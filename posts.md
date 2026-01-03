---
layout: list
title: Posts
description: >
  Posts, trying to be informative if not always exact.
grouped: true
---

<ul>
   {% for post in site.posts %}
    {% unless post.categories contains 'writing' %}
      <li>
        <a href="{{ post.url }}">{{ post.title }}</a>
        {% assign words = post.content | number_of_words %}
        {% assign reading_time = words | divided_by: 200 %}
        <span class="reading-time"> ({{ post.content | reading_time }})</span>
      </li>
    {% endunless %}
  {% endfor %}
</ul>
