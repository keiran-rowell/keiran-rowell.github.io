---
layout: page
title: Interactive Demos
permalink: /interactive/
---

Hands-on computational chemistry and structural bioinformatics tools in your browser.
{:.faded}

- 🧬 Rare codon viewer: [map synonymous codon rarity onto protein structure](https://keiran-rowell.github.io/assets/interactive/codon-rarity-viewer/) 


{% for post in site.categories.interactive %}
- [{{ post.title }}]({{ post.url }}) - {{ post.date | date: "%Y-%m-%d" }}
{% endfor %}

## File Structure
```
/assets/
  /interactive/
   /codon-rarity-viewer/
     codon_tables.pkl
     codon_utils.py
     index.html 
```
