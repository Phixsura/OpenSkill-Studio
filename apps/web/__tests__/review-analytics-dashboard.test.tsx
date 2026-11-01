import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReviewAnalyticsDashboard } from "@/components/review-analytics-dashboard";

describe("ReviewAnalyticsDashboard", () => {
  it("renders", () => {
    const { container } = render(
      <ReviewAnalyticsDashboard total={100} avgRating={4.5}
        sentiment={{ positive: 70, neutral: 20, negative: 10, nps: 60 }}
        keywords={[{ word: "great", count: 25 }, { word: "easy", count: 18 }]}
        replyRate={85} />
    );
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("4.5 ★");
    expect(container.textContent).toContain("60");
    expect(container.textContent).toContain("85%");
    expect(container.textContent).toContain("great (25)");
    expect(container.textContent).toContain("Positive");
  });
});
