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
        <span class="reading-time"> ({{ reading_time }} min)</span>
      </li>
    {% endunless %}
  {% endfor %}
</ul>


<aside class="message">
  <div style="display: flex; align-items: flex-start; color: inherit;">
    <i class="icon-rss" style="font-size: 1.5rem; margin-right: 1rem; margin-top: 0.2rem; color: var(--accent-color);"></i>
    <span>
      <strong>Feed Subscription</strong><br>
      Follow my long-form science posts via <a href="{{ '/feed.xml' | relative_url }}" style="text-decoration: underline; color: inherit;">RSS</a>.
      
      <div style="margin-top: 0.8rem;">
        <a href="https://mastodon.social/@keiran_rowell" class="project-card-link" style="font-size: 0.8rem; padding: 4px 10px; background: var(--accent-color); color: var(--bg-color) !important; border-radius: 4px; text-decoration: none; display: inline-flex; align-items: center; gap: 6px;">
          <i class="icon-mastodon"></i> Follow on Fediverse
        </a>
      </div>
    </span>
  </div>
</aside>
