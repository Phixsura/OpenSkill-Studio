import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeveloperScoreCard } from "@/components/developer-score-card";

const mockDimensions = [
  { name: "code_quality", value: 92, weight: 0.25, description: "Tests and lint" },
  { name: "community", value: 75, weight: 0.20, description: "Engagement" },
  { name: "responsiveness", value: 88, weight: 0.20, description: "Response time" },
  { name: "reliability", value: 96, weight: 0.20, description: "Uptime" },
  { name: "adoption", value: 65, weight: 0.15, description: "Downloads" },
];

const mockTips = [
  { dimension: "adoption", tip: "Improve adoption: increase visibility with tags and descriptions", current: 65 },
  { dimension: "community", tip: "Improve community: respond to more reviews", current: 75 },
];

describe("DeveloperScoreCard", () => {
  it("renders score and grade", () => {
    const { container } = render(
      <DeveloperScoreCard developerName="Alice" overallScore={85} grade="A"
        dimensions={mockDimensions} tips={mockTips} />
    );
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("85");
    expect(container.textContent).toContain("/100");
  });

  it("renders dimension bars", () => {
    const { container } = render(
      <DeveloperScoreCard developerName="Bob" overallScore={70} grade="B"
        dimensions={mockDimensions} tips={[]} />
    );
    expect(container.textContent).toContain("code quality");
    expect(container.textContent).toContain("92/100");
    expect(container.textContent).toContain("reliability");
    expect(container.textContent).toContain("96/100");
  });

  it("renders improvement tips", () => {
    const { container } = render(
      <DeveloperScoreCard developerName="Carol" overallScore={60} grade="C"
        dimensions={mockDimensions} tips={mockTips} />
    );
    expect(container.textContent).toContain("Improvement Tips");
    expect(container.textContent).toContain("adoption");
    expect(container.textContent).toContain("reviews");
  });
});
