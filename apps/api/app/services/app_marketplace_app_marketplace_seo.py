"""Marketplace SEO — structured data and meta tags for marketplace pages."""

def build_page_seo(*, page_type: str, title: str, description: str,
                     url: str, image: str | None = None) -> dict:
    return {
        "title": f"{title} | OpenSkill Marketplace",
        "description": description[:160],
        "canonical_url": url,
        "og": {"title": title, "description": description[:160], "type": "website",
               "url": url, "image": image},
        "structured_data": {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication" if page_type == "app" else "WebPage",
            "name": title, "description": description[:160], "url": url,
        },
    }

def build_app_structured_data(*, app: dict, rating: float, review_count: int) -> dict:
    return {
        "@context": "https://schema.org", "@type": "SoftwareApplication",
        "name": app.get("name"), "description": app.get("description", "")[:160],
        "applicationCategory": app.get("category", ""),
        "aggregateRating": {"@type": "AggregateRating", "ratingValue": rating,
                             "reviewCount": review_count, "bestRating": 5},
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
    }
