"""Read public X post text, including X Article text, without the paid API."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from typing import Any


TWEET_RESULT_QUERY_ID = "SgZWKwvBiOKrSC0QeOGvXw"
TWEET_RESULT_OPERATION = "TweetResultByRestId"

FEATURES = {
    "creator_subscriptions_tweet_preview_api_enabled": True,
    "premium_content_api_read_enabled": True,
    "communities_web_enable_tweet_community_results_fetch": True,
    "c9s_tweet_anatomy_moderator_badge_enabled": True,
    "responsive_web_grok_analyze_button_fetch_trends_enabled": True,
    "responsive_web_grok_analyze_post_followups_enabled": True,
    "rweb_cashtags_composer_attachment_enabled": True,
    "responsive_web_jetfuel_frame": True,
    "responsive_web_grok_share_attachment_enabled": True,
    "responsive_web_grok_annotations_enabled": True,
    "articles_preview_enabled": True,
    "responsive_web_edit_tweet_api_enabled": True,
    "rweb_conversational_replies_downvote_enabled": True,
    "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
    "view_counts_everywhere_api_enabled": True,
    "longform_notetweets_consumption_enabled": True,
    "responsive_web_twitter_article_tweet_consumption_enabled": True,
    "content_disclosure_indicator_enabled": True,
    "content_disclosure_ai_generated_indicator_enabled": True,
    "responsive_web_grok_show_grok_translated_post": True,
    "responsive_web_grok_analysis_button_from_backend": True,
    "post_ctas_fetch_enabled": True,
    "rweb_cashtags_enabled": True,
    "freedom_of_speech_not_reach_fetch_enabled": True,
    "standardized_nudges_misinfo": True,
    "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
    "longform_notetweets_rich_text_read_enabled": True,
    "longform_notetweets_inline_media_enabled": True,
    "profile_label_improvements_pcf_label_in_post_enabled": True,
    "responsive_web_profile_redirect_enabled": True,
    "rweb_tipjar_consumption_enabled": True,
    "verified_phone_label_enabled": True,
    "responsive_web_grok_image_annotation_enabled": True,
    "responsive_web_grok_imagine_annotation_enabled": True,
    "responsive_web_grok_community_note_auto_translation_is_enabled": True,
    "responsive_web_graphql_skip_user_profile_image_extensions_enabled": True,
    "responsive_web_graphql_timeline_navigation_enabled": True,
}

FIELD_TOGGLES = {
    "withArticleRichContentState": True,
    "withArticlePlainText": True,
    "withArticleSummaryText": True,
    "withArticleVoiceOver": True,
    "withGrokAnalyze": False,
    "withDisallowedReplyControls": True,
    "withPayments": False,
    "withAuxiliaryUserLabels": True,
}


def get_text(url: str, headers: dict[str, str] | None = None) -> str:
    request = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8", errors="replace")


def get_json(url: str, headers: dict[str, str]) -> dict[str, Any]:
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def normalize_x_url(value: str) -> tuple[str, str]:
    match = re.search(r"(?:x|twitter)\.com/([^/]+)/status/(\d+)", value)
    if not match:
        raise ValueError("Expected an X/Twitter status URL.")

    handle, status_id = match.groups()
    return f"https://x.com/{handle}/status/{status_id}", status_id


def extract_bearer_token(html: str) -> str:
    match = re.search(
        r"https://abs\.twimg\.com/responsive-web/client-web/main\.[^\"']+\.js",
        html,
    )
    if not match:
        raise RuntimeError("Could not find X main JavaScript bundle.")

    bundle = get_text(match.group(0), headers={"User-Agent": "Mozilla/5.0"})
    token = re.search(r"AAAAA[A-Za-z0-9%_-]+", bundle)
    if not token:
        raise RuntimeError("Could not find X bearer token in JavaScript bundle.")

    return urllib.parse.unquote(token.group(0))


def extract_guest_token(html: str) -> str:
    match = re.search(r'document\.cookie="gt=([^;]+);', html)
    if not match:
        raise RuntimeError("Could not find logged-out guest token.")

    return match.group(1)


def fetch_tweet_result(status_url: str, tweet_id: str) -> dict[str, Any]:
    html = get_text(status_url, headers={"User-Agent": "Mozilla/5.0"})
    bearer_token = extract_bearer_token(html)
    guest_token = extract_guest_token(html)

    variables = {
        "tweetId": tweet_id,
        "includePromotedContent": True,
        "withBirdwatchNotes": False,
        "withVoice": True,
        "withCommunity": True,
    }
    params = urllib.parse.urlencode(
        {
            "variables": json.dumps(variables, separators=(",", ":")),
            "features": json.dumps(FEATURES, separators=(",", ":")),
            "fieldToggles": json.dumps(FIELD_TOGGLES, separators=(",", ":")),
        }
    )
    url = (
        "https://x.com/i/api/graphql/"
        f"{TWEET_RESULT_QUERY_ID}/{TWEET_RESULT_OPERATION}?{params}"
    )
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {bearer_token}",
        "referer": status_url,
        "user-agent": "Mozilla/5.0",
        "x-guest-token": guest_token,
        "x-twitter-active-user": "yes",
        "x-twitter-client-language": "en",
    }
    return get_json(url, headers=headers)


def simplify(result: dict[str, Any]) -> dict[str, Any]:
    tweet = result["data"]["tweetResult"]["result"]
    legacy = tweet.get("legacy", {})
    user = tweet.get("core", {}).get("user_results", {}).get("result", {})
    user_core = user.get("core", {})
    article = (
        tweet.get("article", {})
        .get("article_results", {})
        .get("result")
    )

    output = {
        "tweet_id": tweet.get("rest_id"),
        "author_name": user_core.get("name"),
        "author_handle": user_core.get("screen_name"),
        "created_at": legacy.get("created_at"),
        "tweet_text": legacy.get("full_text"),
        "article": None,
    }

    if article:
        output["article"] = {
            "id": article.get("rest_id"),
            "title": article.get("title"),
            "preview_text": article.get("preview_text"),
            "summary_text": article.get("summary_text"),
            "plain_text": article.get("plain_text"),
            "block_count": len(article.get("content_state", {}).get("blocks", [])),
        }

    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="Public X/Twitter status URL")
    args = parser.parse_args()

    status_url, tweet_id = normalize_x_url(args.url)
    print(
        json.dumps(
            simplify(fetch_tweet_result(status_url, tweet_id)),
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
