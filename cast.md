---
title: The cast
permalink: /cast/
description: The recurring characters in the Cypher Rants doodles — the classic cryptography placeholders, drawn as people.
---
<div class="rule"><span><span class="mark">the cast</span></span><span class="muted">they show up whenever a rant needs someone to talk to</span></div>
<section class="cast-section" id="cast">
<div class="cast-grid">
{% for c in site.data.cast.cast %}<div class="member" id="cast-{{ c.name }}">{% include doodle.html who=c.name size=150 %}<span class="hand">{{ c.name }}</span><span class="muted">{{ c.role }}</span></div>
{% endfor %}</div>
</section>
