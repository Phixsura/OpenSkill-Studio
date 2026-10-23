import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ListingPreviewCard } from "@/components/listing-preview-card";

describe("ListingPreviewCard", () => {
  it("renders preview", () => {
    const { container } = render(
      <ListingPreviewCard
        preview={{ name: "Slack Bot", icon: "💬", tagline: "Best Slack", rating: 4.8,
                   installsDisplay: "50,000", priceDisplay: "Free", verified: true, category: "communication" }}
        completeness={{ pct: 100, ready: true, filled: 7, total: 7 }} />
    );
    expect(container.textContent).toContain("Slack Bot");
    expect(container.textContent).toContain("Best Slack");
    expect(container.textContent).toContain("50,000");
    expect(container.textContent).toContain("Free");
    expect(container.textContent).toContain("100%");
    expect(container.textContent).toContain("7/7");
  });
});
