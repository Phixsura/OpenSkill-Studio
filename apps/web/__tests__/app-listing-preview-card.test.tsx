import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppListingPreviewCard } from "@/components/app-listing-preview-card";

describe("AppListingPreviewCard", () => {
  const card = { name: "Auth SDK", tagline: "Authentication made easy", developer: "Alice",
    rating: 4.7, stars: "★★★★★", install_count: "5,000", price_label: "Free", category: "security" };
  const completeness = { pct: 100, completed: 6, total: 6 };
  it("renders", () => {
    const { container } = render(
      <AppListingPreviewCard card={card} completeness={completeness} />
    );
    expect(container.textContent).toContain("Listing Preview");
    expect(container.textContent).toContain("Auth SDK");
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("Free");
    expect(container.textContent).toContain("★★★★★");
    expect(container.textContent).toContain("6/6");
  });
});
