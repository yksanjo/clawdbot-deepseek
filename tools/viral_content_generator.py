#!/usr/bin/env python3
"""
🚀 Viral Content Generator for Claude vs GPT Feud
Generates tweet threads, LinkedIn posts, and Hacker News angles.
"""

import random
from datetime import datetime

TEMPLATES = {
    "tweet_threads": [
        {
            "hook": "Claude and GPT are fighting again.\n\nMeanwhile, I'm over here paying $5/month for AI that remembers everything and doesn't rate limit me.",
            "body": [
                "The AI feud is exhausting.",
                "One month: 'Claude is better!'",
                "Next month: 'GPT crushed it!'",
                "Meanwhile my DeepSeek setup:",
                "→ 50x cheaper",
                "→ Self-hosted (no outages)",
                "→ Persistent memory",
                "→ No corporate drama",
            ],
            "cta": "Sometimes the best move is opting out of the fight.\n\nBuild on open source. Sleep better."
        },
        {
            "hook": "Hot take: The Claude vs GPT feud is a distraction.\n\nSmart developers are building on the third option.",
            "body": [
                "Everyone's arguing about Claude 3.5 vs GPT-4o.",
                "I'm just here with my:",
                "✓ $5/month AI bill (was $200)",
                "✓ Self-hosted model",
                "✓ No API rate limits",
                "✓ Actually remembers context",
                "The secret? DeepSeek + clawdbot.",
            ],
            "cta": "Let them fight. You have shipping to do.\n\n👇"
        },
        {
            "hook": "My CI pipeline doesn't care if Claude or GPT 'wins'.\n\nIt uses both. And DeepSeek. And local models.",
            "body": [
                "Yesterday Claude API had issues.",
                "I switched to GPT-4 in one line of config.",
                "Today GPT is slow.",
                "Switched to DeepSeek.",
                "This is what 'model-agnostic' means:",
                "→ No lock-in",
                "→ Always use best/cheapest",
                "→ Corporate drama ≠ your problem",
            ],
            "cta": "Your infrastructure should be antifragile."
        }
    ],
    
    "linkedin_posts": [
        {
            "title": "Why I Stopped Caring About the Claude vs GPT Debate",
            "body": """The AI space feels like a reality show lately.

Claude vs GPT. Anthropic vs OpenAI. Model this, benchmark that.

Meanwhile, I've been quietly building on a third path:

🔹 Self-hosted AI (DeepSeek)
🔹 50x cost reduction  
🔹 Zero API dependencies
🔹 Persistent memory that actually works

The feud is a distraction.

Smart engineering teams are building infrastructure that works with ANY model—today's best, tomorrow's cheaper alternative, next year's breakthrough.

Model-agnostic architecture isn't just smart. It's necessary.

What are you building on?"""
        },
        {
            "title": "The Hidden Cost of AI Provider Lock-in",
            "body": """Yesterday Claude API had an outage.

Last month, GPT-4 prices increased for enterprise users.

Three months ago, a model I relied on was deprecated.

This is the reality of centralized AI.

Meanwhile, our team runs agentic-ci with:
✓ Multi-model support (Claude, GPT, DeepSeek, local)
✓ One-line provider switching
✓ Cost optimization across providers
✓ Zero downtime during API issues

The Claude vs GPT feud proves one thing: you can't bet on a single provider.

Portability is the feature.

What's your failover strategy?"""
        }
    ],
    
    "hackernews_angles": [
        {
            "title": "Show HN: clawdbot-deepseek – Self-hosted AI memory, 50x cheaper than GPT-4",
            "angle": "The Claude vs GPT debate misses the point. Here's a third option that's actually affordable."
        },
        {
            "title": "Show HN: agentic-ci – CI that works with any LLM (Claude, GPT, DeepSeek)",
            "angle": "Don't get locked into one AI provider for your CI pipeline. Switch in one config line."
        },
        {
            "title": "Ask HN: Are you worried about AI provider lock-in?",
            "angle": "The Claude/GPT feud made me realize how risky single-provider dependencies are."
        }
    ],
    
    "reddit_posts": {
        "r/selfhosted": "Escaped the Claude vs GPT drama with self-hosted DeepSeek. $5/month vs $200. AMA.",
        "r/devops": "Built model-agnostic CI that switches between Claude/GPT/DeepSeek automatically. Here's why.",
        "r/programming": "The Claude vs GPT feud is exhausting. I built something that doesn't care who wins."
    }
}

def generate_tweet_thread():
    """Generate a viral tweet thread."""
    thread = random.choice(TEMPLATES["tweet_threads"])
    
    print("🐦 TWEET THREAD")
    print("=" * 50)
    print(f"\n1/{len(thread['body']) + 2}\n{thread['hook']}\n")
    
    for i, tweet in enumerate(thread['body'], 2):
        print(f"{i}/{len(thread['body']) + 2}\n{tweet}\n")
    
    print(f"{len(thread['body']) + 2}/{len(thread['body']) + 2}\n{thread['cta']}\n")

def generate_linkedin():
    """Generate a LinkedIn post."""
    post = random.choice(TEMPLATES["linkedin_posts"])
    
    print("💼 LINKEDIN POST")
    print("=" * 50)
    print(f"\n{post['title']}\n")
    print(post['body'])
    print("\n" + "=" * 50)

def generate_hn():
    """Generate Hacker News title ideas."""
    print("📰 HACKER NEWS ANGLES")
    print("=" * 50)
    for post in TEMPLATES["hackernews_angles"]:
        print(f"\n• {post['title']}")
        print(f"  Angle: {post['angle']}")

def generate_all():
    """Generate content for all platforms."""
    generate_tweet_thread()
    print("\n")
    generate_linkedin()
    print("\n")
    generate_hn()
    
    print("\n📱 REDDIT POSTS")
    print("=" * 50)
    for subreddit, title in TEMPLATES["reddit_posts"].items():
        print(f"\n{subreddit}:")
        print(f"  '{title}'")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "twitter":
            generate_tweet_thread()
        elif sys.argv[1] == "linkedin":
            generate_linkedin()
        elif sys.argv[1] == "hn":
            generate_hn()
        else:
            generate_all()
    else:
        generate_all()
