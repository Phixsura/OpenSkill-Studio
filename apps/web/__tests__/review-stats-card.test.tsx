import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReviewStatsCard } from "@/components/review-stats-card";

describe("ReviewStatsCard", () => {
  it("renders stats", () => {
    const { container } = render(
      <ReviewStatsCard total={100} avgRating={4.2} stars="★★★★☆"
        distribution={{ 1: 5, 2: 10, 3: 15, 4: 30, 5: 40 }}
        nps={25} recommendationPct={70}
        sentiment={{ positive: 70, neutral: 15, negative: 15 }} />
    );
    expect(container.textContent).toContain("4.2");
    expect(container.textContent).toContain("★★★★☆");
    expect(container.textContent).toContain("100 reviews");
    expect(container.textContent).toContain("NPS:");
    expect(container.textContent).toContain("25");
    expect(container.textContent).toContain("70% recommend");
  });
});
