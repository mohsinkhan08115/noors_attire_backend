# app/schemas/homepage_schema.py
#
# Configuration for the customer-facing homepage — lets the admin edit
# the announcement bar, hero content, and which sections show (and in
# what order) without a code change.

from pydantic import BaseModel, Field
from typing import Optional, List


class AnnouncementConfig(BaseModel):
    enabled: bool = True
    text: str = (
        "✨ FREE EXPRESS SHIPPING ON ALL ORDERS OVER PKR 5,000 | "
        "AUTHENTIC PASHTUN HERITAGE"
    )
    link: Optional[str] = None
    background_style: str = "dark"  # "dark" | "primary" | "accent"
    start_at: Optional[str] = None  # ISO datetime — omit to run immediately
    end_at: Optional[str] = None  # ISO datetime — omit to run indefinitely


class HeroConfig(BaseModel):
    badge_text: str = "ROYAL HERITAGE COLLECTION 2026"
    headline: str = "Noor's Attire"
    subheadline: str = "Elegance in Every Thread — Authentic Pashtun Craftsmanship"
    image_url: Optional[str] = None
    primary_cta_label: str = "EXPLORE DRESSES"
    primary_cta_category: str = "pashtun_dress"  # "pashtun_dress" | "paint_shirt" | "all"
    secondary_cta_label: str = "PAINT SHIRTS"
    secondary_cta_category: str = "paint_shirt"


class HomepageSection(BaseModel):
    key: str
    enabled: bool = True
    order: int


DEFAULT_SECTION_KEYS = [
    "categories",
    "featured",
    "new_arrivals",
    "bestsellers",
    "editorial",
    "showcase",
    "brand_story",
    "trust_badges",
    "testimonials",
    "social_gallery",
    "newsletter",
]


class HomepageConfig(BaseModel):
    announcement: AnnouncementConfig = Field(default_factory=AnnouncementConfig)
    hero: HeroConfig = Field(default_factory=HeroConfig)
    sections: List[HomepageSection] = Field(
        default_factory=lambda: [
            HomepageSection(key=k, enabled=True, order=i)
            for i, k in enumerate(DEFAULT_SECTION_KEYS)
        ]
    )
    updated_at: Optional[str] = None
