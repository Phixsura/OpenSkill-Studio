import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FeedbackSummaryCard } from "@/components/feedback-summary-card";

describe("FeedbackSummaryCard", () => {
  it("renders summary", () => {
    const { container } = render(
      <FeedbackSummaryCard count={100} avgRating={4.2} nps={45}
        byRating={{ "1": 5, "2": 10, "3": 15, "4": 30, "5": 40 }} />
    );
    expect(container.textContent).toContain("User Feedback");
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("4.2");
    expect(container.textContent).toContain("+45");
    expect(container.textContent).toContain("5★");
    expect(container.textContent).toContain("40");
  });
});
