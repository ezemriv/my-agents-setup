---
name: x-article-reader
description: Extract and summarize the full text of public X/Twitter Article posts from x.com or twitter.com status URLs. Use when the user shares an X link and asks Codex to read it, summarize it, extract the article text, inspect the content, or avoid manual copy-paste. Especially useful for X posts whose visible tweet body is only a t.co link to an X Article.
---

# X Article Reader

## Workflow

Use the bundled script first for public status URLs:

```bash
python3 ~/.codex/skills/x-article-reader/scripts/read_x_article.py '<x-status-url>'
```

The script:

1. Loads the public status page.
2. Extracts X's logged-out guest token and current web bearer token.
3. Calls X's logged-out GraphQL `TweetResultByRestId` endpoint with article fields enabled.
4. Returns JSON containing tweet metadata plus article title, preview, summary, plain text, and content block count when present.

## Output Handling

If `article.plain_text` exists, treat it as the full readable article body.

If `article` is null, fall back to `tweet_text`; the post may be a normal tweet, deleted, protected, restricted, or not an X Article.

When summarizing, report:

- author name and handle
- tweet wrapper text if relevant
- article title
- extracted character count
- concise summary of the article

Avoid pasting the entire article unless the user explicitly asks for full extraction.

## Safety Notes

Use this only for public X content. The script does not require user cookies for tested public article posts. If a link fails because X requires login, ask before using any cookie-backed approach, and treat cookies such as `auth_token` and `ct0` as secrets.
