"""THE FINAL PLATFORM AGGREGATOR — combines EVERYTHING into one complete developer platform view."""

def build_final_platform_view(*, marketplace: dict, developer: dict, infrastructure: dict,
                                  community: dict) -> dict:
    return {
        "page_type": "complete_platform",
        "marketplace": marketplace,
        "developer_tools": developer,
        "infrastructure": infrastructure,
        "community": community,
        "platform_version": "1.0.0",
        "feature_count": sum(len(v) if isinstance(v, (list, dict)) else 1
                             for section in [marketplace, developer, infrastructure, community]
                             for v in section.values()),
    }
