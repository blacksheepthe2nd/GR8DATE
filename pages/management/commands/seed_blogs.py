import io
from pathlib import Path
from urllib.request import urlopen, Request

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings

from pages.models import Blog


def fetch_image(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=30) as r:
        return r.read()


def ensure_media_dir() -> Path:
    media_root = Path(settings.MEDIA_ROOT)
    (media_root / "blog").mkdir(parents=True, exist_ok=True)
    return media_root


POSTS = [
    {
        "title": "Why GR8DATE is Totally Free for Everyone",
        "slug": "why-gr8date-is-totally-free-for-everyone",
        "summary": "GR8DATE removes paywalls so anyone can connect, browse and message—free. Here’s why cost should never be a barrier to finding meaningful connections.",
        "hero_url": "https://images.unsplash.com/photo-1529336953121-4d9d06f34d19?q=80&w=1600&auto=format&fit=crop",
        "hero_name": "free-for-all.jpg",
        "status": Blog.Status.PUBLISHED,
        "published_at": lambda: timezone.now(),
        "content": """
In a digital age where almost every swipe, match, or message comes with a price tag, it can feel like online dating has turned into a marketplace rather than a meeting place. People sign up hoping to find companionship, but instead they discover a labyrinth of subscriptions, in-app purchases, and constant upsells. At GR8DATE, we decided to do things differently. We believe dating should be free, inclusive, and accessible to everyone — no matter who you are or where you come from.

## The Problem With Paywalls
If you’ve ever tried other dating platforms, you’ll know the story: you download the app or sign up on a website, only to find that the basic features you need — like seeing who liked you, sending a message, or even reading a message you received — are hidden behind a subscription. While some companies argue that charging users ensures “quality matches” or “serious intent,” the reality is that paywalls exclude people. Not everyone can afford monthly fees just to talk to someone new, and that inequality creates an unnecessary barrier to love and connection.

Paywalls also distort the experience. Instead of focusing on authenticity and compatibility, people are pushed toward mechanics that maximise revenue: limited likes, “boosts,” or “super messages.” Dating becomes a game of who pays more, not who fits better.

## Why GR8DATE Took a Different Path
From the beginning our mission has been to open doors, not close them. We asked: what if dating was truly free? What if everyone had the same chance to create a profile, browse, match, and message without worrying about being charged?

That’s why GR8DATE is totally free — not “free until you want to actually use it,” not “free with pop-ups everywhere,” but genuinely free. You won’t be asked for credit card details. You won’t have to upgrade to unlock features. What you see is what you get: a platform built for people, not paywalls.

## Inclusivity Matters
Relationships come in many forms. Some people are looking for long-term partners, others for companionship, friendship, or something casual. By keeping our platform free, we ensure that every person — young or old, shy or confident, affluent or just starting out — has equal opportunity to connect. Price should never be the filter that decides who gets to be seen.

## Building Trust Without Transactions
One of the most important ingredients in any relationship is trust. When apps charge for every little interaction, the relationship between platform and user becomes transactional. That’s not trust; that’s a business deal. GR8DATE doesn’t need to nickel-and-dime you to keep you around. We’re focused on making the experience enjoyable, intuitive, and safe.

## Safety Still Comes First
Free does not mean careless. We invest in safety tooling, profile checks, reporting features, and moderation so the community remains respectful. Our success isn’t tied to your wallet — it’s tied to your happiness and wellbeing on the platform.

## Real Stories, Real People
Early users repeatedly tell us how refreshing it feels to use a platform without constant upsells. “It feels more human,” one user said. “I’m not wondering if the person I’m talking to has paid for extra features or if they’re only half-committed. We’re all on the same level.”

## What This Means for the Future
Free dating doesn’t mean low-quality dating. It means we’re investing in smarter discovery, thoughtful design, and better community tools to make sure your experience feels genuine. As GR8DATE grows, our focus stays the same: a safe, equal, truly free space to meet others.

**In short: GR8DATE is totally free because love shouldn’t come with a price tag.** When the playing field is level, connections are more authentic and more meaningful. Whether you’re new to online dating or have tried every app under the sun, we’d love you to experience what dating feels like when cost is no longer a barrier.
""".strip(),
    },
    {
        "title": "Modern Dating: Pros and Cons of Going Online",
        "slug": "modern-dating-pros-and-cons-online",
        "summary": "Online dating offers reach, speed and flexibility — but also burnout and noise. Here’s a balanced, human take on making it work for you.",
        "hero_url": "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?q=80&w=1600&auto=format&fit=crop",
        "hero_name": "modern-dating.jpg",
        "status": Blog.Status.PUBLISHED,
        "published_at": lambda: timezone.now(),
        "content": """
A decade ago, the idea of meeting someone online carried a stigma. Today, it’s the norm. Apps and sites promise to make dating faster and smarter than ever, and for many people they do. But like any powerful tool, online dating magnifies both strengths and weaknesses. Here’s a human look at what works — and what doesn’t — and how to keep your energy and optimism intact.

## The Pros
**Wider reach.** Online dating breaks geography. If you live in a small town, belong to a niche community, or keep unusual hours, the internet opens new doors.  
**Efficiency.** Filters and prompts surface people who share your interests or goals. That can save months of guesswork.  
**Openness.** Stating what you want — serious, casual, friendship — reduces awkwardness and mismatched expectations.  
**Flexibility.** You date on your own time. Lunch break? Late night? Travelling? Your social life can fit around real life.

## The Cons
**Choice overload.** An endless feed can make everyone feel replaceable. It’s easy to forget there’s a person behind each profile.  
**Surface bias.** Photos dominate first impressions; great personalities can be skipped because a picture didn’t grab attention.  
**Safety concerns.** Catfishing and scams exist. Platforms need robust safety tools and responsive moderation.  
**Emotional burnout.** The cycle of swiping, chatting, ghosting and repeating can be draining.

## A Better Way to Use Online Dating
Set intentions, not rules. Know what you want this month, not forever.  
Protect your energy: limit daily swipes, take breaks, and move promising chats to a coffee within a week or two.  
Write a profile that sounds like you — specific, playful, clear. Specificity is attractive: it gives people something to respond to.

## How GR8DATE Helps
We designed GR8DATE to amplify the pros and reduce the cons:
- **No paywalls** lowers frustration and levels the field.  
- **Safety features** and reporting build trust.  
- **Smarter discovery** reduces noise and surfaces people who actually match your vibe.  
- **A community-first ethos** encourages conversation over gamified swiping.

**Bottom line:** online dating is here to stay. Approach it with intention and self-care, and it can expand your world without overwhelming it.
""".strip(),
    },
    {
        "title": "Complete Your Profile to Unlock GR8DATE’s Matching Power",
        "slug": "complete-your-profile-for-better-matches",
        "summary": "Profiles with photos and details get more views and better matches. Here’s how to make yours shine before our full matching launches.",
        "hero_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=1600&auto=format&fit=crop",
        "hero_name": "complete-profile.jpg",
        "status": Blog.Status.PUBLISHED,
        "published_at": lambda: timezone.now(),
        "content": """
Think of your GR8DATE profile as your introduction at a party. If you wore a mask and never spoke, nobody would know who you are. Online, your profile *is* your first impression, and it matters more than you might think. A complete profile isn’t vanity — it’s clarity.

## Why Complete Profiles Win
People are drawn to transparency. Profiles with multiple photos, filled-out bios and clear preferences get more views and better conversations. A blank profile suggests you’re not serious; a detailed one sparks curiosity.

## What to Fill Out (and Why)
**Photos.** Add at least three: one clear face photo, one full-body, and one showing a hobby or context (cooking, hiking, music). Together they tell a story.  
**About me.** Two or three short paragraphs with specifics beat one generic line. Mention interests, routines, and a small quirk — specifics are memorable.  
**What you’re seeking.** Be honest about the kind of connection you want. Alignment saves time and avoids mismatched expectations.  
**Lifestyle details.** Hobbies, pets, travel, kids, smoking — these are useful signals for compatibility.  
**Tagline.** A short, playful line that captures your vibe helps others start a conversation.

## Tips to Stand Out
Show variety in photos; smile at least once; avoid heavy filters; write like you speak; keep it positive; ask a question in your bio (“What’s your go-to beach walk?”) to invite replies.

## How GR8DATE’s Matching Will Use This
When we roll out our full matching, it will use the details you provide — interests, lifestyle, intent — to suggest compatible people. The more you share, the smarter the recommendations. Think of it as giving the algorithm all the puzzle pieces.

## Mistakes to Avoid
Only one blurry photo, copy-paste bios, negativity, or leaving critical fields blank. Your profile is the handshake before the hello — make it count.

**Take ten minutes today to round out your profile.** Future you (and your future matches) will thank you.
""".strip(),
    },
]


class Command(BaseCommand):
    help = "Seeds the database with three GR8DATE blog posts and downloads hero images."

    def handle(self, *args, **options):
        ensure_media_dir()
        created = 0
        updated = 0

        for p in POSTS:
            slug = p["slug"]
            defaults = {
                "title": p["title"],
                "summary": p["summary"],
                "content": p["content"],
                "status": p["status"],
                "published_at": p["published_at"](),
            }

            obj, was_created = Blog.objects.get_or_create(slug=slug, defaults=defaults)
            if not was_created:
                for k, v in defaults.items():
                    setattr(obj, k, v)
                obj.save()
                updated += 1
            else:
                created += 1

            try:
                img_bytes = fetch_image(p["hero_url"])
                obj.hero_image.save(p["hero_name"], ContentFile(img_bytes), save=True)
                self.stdout.write(self.style.SUCCESS(f"Attached hero image: blog/{p['hero_name']}"))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Could not download hero image for '{obj.title}': {e}"))

            self.stdout.write(self.style.SUCCESS(f"{'Created' if was_created else 'Updated'}: {obj.title}"))

        self.stdout.write(self.style.SUCCESS(f"Done. Created: {created}, Updated: {updated}"))
