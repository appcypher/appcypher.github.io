# Cypher Rants

Personal Jekyll blog for https://appcypher.github.io. Dark by default, with an optional light theme. No published sample posts.

## Publish on GitHub Pages

Create the public repository `appcypher/appcypher.github.io` and push these files to `main`. In Settings → Pages, select “Deploy from a branch”, choose `main` and `/ (root)`, and save. GitHub builds Jekyll automatically.

## Write a post

Copy `_drafts/first-rant.md` to `_posts/YYYY-MM-DD-your-post-title.md`. Set the title and description in its front matter, replace the body with your Markdown, and commit and push. Use today's date or an earlier date to publish immediately. Future-dated posts need a rebuild after their publication date. Files under `_drafts` are not rendered, but are visible in the public source repository; keep private drafts elsewhere.

## Preview locally

```sh
bundle install
bundle exec jekyll serve
```

Open http://localhost:4000. Add `--drafts` to preview drafts locally. Update `about.md` for your bio, and `_config.yml` for site details.
