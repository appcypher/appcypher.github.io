---
title: The cast
permalink: /cast/
description: The recurring characters in the Cypher Rants doodles — the classic cryptography placeholders, drawn as people.
---
<div class="rule"><span><span class="mark">the cast</span></span><span class="muted">they show up whenever a rant needs someone to talk to</span></div>
<section class="cast-intro">
<p>Alice and Bob have been standing in for "two parties who want to talk" since the 1978 RSA paper, and the rest of the cast accreted over decades of protocol papers: each name is a mnemonic for a role. They appear in the doodles by those roles — if a post is about an eavesdropper, it's eve.</p>
</section>
<section class="cast-section" id="cast">
<div class="cast-grid">
{% for c in site.data.cast.cast %}<div class="member" id="cast-{{ c.name }}">{% include doodle.html who=c.name size=150 %}<span class="hand">{{ c.name }}</span><span class="muted">{{ c.role }}</span></div>
{% endfor %}</div>
</section>
