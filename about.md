---
title: About
permalink: /about/
description: Meet Stephen Akinyemi, also known as appcypher, and the cast of characters that show up in the doodles.
---
<div class="rule"><span><span class="mark">about</span></span><span class="muted">behind the rants</span></div>
<section class="about">
<div class="about-text">
<h1>Behind the rants.</h1>
<p>I'm Stephen Akinyemi, also known as <span class="mark">appcypher</span>.</p>
<p>Cypher Rants is my corner of the internet for things I'm building, lessons along the way, and ideas I want to think through in writing.</p>
<p class="chips"><a class="chip pen" href="https://github.com/appcypher">github — @appcypher ↗</a><a class="chip pen" href="https://x.com/theappcypher">x — @theappcypher ↗</a></p>
</div>
<div class="about-portrait">{% include doodle.html who="stephen" size=220 %}<span class="hand">that's me, more or less</span></div>
</section>
<section class="cast-section" id="cast">
<div class="rule"><span><span class="mark">the cast</span></span><span class="muted">they show up whenever a rant needs someone to talk to</span></div>
<div class="cast-grid">
{% for c in site.data.cast.cast %}<div class="member" id="cast-{{ c.name }}">{% include doodle.html who=c.name size=150 %}<span class="hand">{{ c.name }}</span><span class="muted">{{ c.role }}</span></div>
{% endfor %}</div>
</section>
