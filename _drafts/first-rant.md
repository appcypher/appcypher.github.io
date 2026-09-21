---
title: Your first rant
description: Replace this with a short introduction to your post.
cover: stephen
published: false     # reference sheet, not a post: never builds, not even with --drafts
# rant: true        # marks the post as a rant: RANT stamp on the cover, "rant" chip on the card
# mood: rant        # use the author's furious doodle as the cover
# tags: [jekyll]
---
Write your first post here. This draft stays unpublished until you move it to `_posts/YYYY-MM-DD-your-post-title.md` with the date you want to publish.

A paragraph ending in `{:.aside}` becomes a handwritten sidenote in the margin, like this one.
{:.aside}

## headings become marks

Ordinary Markdown works: **bold**, *italic*, `code`, [links](https://github.com/appcypher), lists, tables and fenced code blocks. Inline glyphs are `:name:` tokens — alice puts the :key: in an :envelope: while :eve: listens :ear:. Any thing from `_includes/doodles/things/` and any cast member works.

{% include react.html who="bob" say="three? that's it?" %}

> note: a blockquote that starts with "note:" turns into a sticky note. Every other blockquote keeps the pen rule.

{% capture d %}
alice: what goes in `_drafts/`?
bob: anything you're not ready to publish. jekyll ignores it until you move it.
{% endcapture %}{% include dialogue.html text=d %}

{% include figure.html scene="empty-state" caption="fig. 1 — a full-width figure breaks out of the text column" %}

Figures take `src="/assets/…png"` for drawings you scan, or `scene="name"` for an SVG in `_includes/doodles/scenes/`. Keep the figure caption a real sentence; it replaces the paragraph the drawing stands in for.
