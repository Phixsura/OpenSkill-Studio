import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReviewInsightsPanel } from "@/components/review-insights-panel";

describe("ReviewInsightsPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ReviewInsightsPanel totalReviews={100} sentimentScore={33.3}
        sentiment={{ positive: 60, negative: 20, neutral: 20 }}
        commonWords={[{ word: "great", count: 25 }, { word: "easy", count: 18 }]}
        topics={{ ui: 30, performance: 15 }} avgRating={4.2} />
    );
    expect(container.textContent).toContain("Review Insights");
    expect(container.textContent).toContain("60");
    expect(container.textContent).toContain("😊");
    expect(container.textContent).toContain("+33.3%");
    expect(container.textContent).toContain("great (25)");
    expect(container.textContent).toContain("ui (30)");
    expect(container.textContent).toContain("⭐ 4.2");
  });
});
