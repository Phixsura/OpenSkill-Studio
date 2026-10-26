import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ListingScoreCard } from "@/components/listing-score-card";

const mockScore = {
  total: 75, maxScore: 100, grade: "B",
  sections: {
    title: { score: 15, max: 15 },
    description: { score: 20, max: 25 },
    media: { score: 15, max: 20 },
    metadata: { score: 15, max: 20 },
    resources: { score: 10, max: 20 },
  },
  suggestions: ["Add at least 3 screenshots", "Add documentation link"],
};

describe("ListingScoreCard", () => {
  it("renders grade and total", () => {
    const { container } = render(<ListingScoreCard score={mockScore} />);
    expect(container.textContent).toContain("B");
    expect(container.textContent).toContain("75/100");
    expect(container.textContent).toContain("75%");
  });

  it("renders section scores", () => {
    const { container } = render(<ListingScoreCard score={mockScore} />);
    expect(container.textContent).toContain("Title");
    expect(container.textContent).toContain("15/15");
    expect(container.textContent).toContain("20/25");
  });

  it("renders suggestions", () => {
    const { container } = render(<ListingScoreCard score={mockScore} />);
    expect(container.textContent).toContain("3 screenshots");
    expect(container.textContent).toContain("documentation link");
  });

  it("handles perfect score", () => {
    const perfect = { ...mockScore, total: 100, grade: "A", suggestions: [] };
    const { container } = render(<ListingScoreCard score={perfect} />);
    expect(container.textContent).toContain("A");
    expect(container.textContent).not.toContain("Suggestions");
  });
});
