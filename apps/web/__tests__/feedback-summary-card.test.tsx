import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FeedbackSummaryCard } from "@/components/feedback-summary-card";

describe("FeedbackSummaryCard", () => {
  it("renders feedback", () => {
    const { container } = render(
      <FeedbackSummaryCard total={100} avgRating={4.2} nps={45}
        promoters={60} detractors={15}
        byCategory={{ ui: { count: 50, avgRating: 4.5 }, api: { count: 30, avgRating: 3.8 } }} />
    );
    expect(container.textContent).toContain("User Feedback");
    expect(container.textContent).toContain("4.2");
    expect(container.textContent).toContain("45");
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("60 promoters");
    expect(container.textContent).toContain("ui");
    expect(container.textContent).toContain("4.5");
  });
});
