---
layout: list
title: Writing 
slug: writing
description: >
  Reflective, personal, evocative, speculative. 
  Not intended as instructional material.
grouped: true
---

<ul>
  {% for post in site.categories.writing %}
    <li>
      <a href="{{ post.url }}">{{ post.title }}</a>
    </li>
  {% endfor %}
</ul>
