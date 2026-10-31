import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-1000th-pair-milestone-card";

describe("1000thPairMilestoneCard", () => {
  it("shows milestone celebration", () => {
    const categories = ["webhooks", "rate_limiting", "authentication", "billing", "monitoring"];
    const { container } = render(<Card pairCount={1000} commitCount={6500} backendTests={6000} frontendTests={2000} totalFiles={4000} categories={categories} achievedAt="2026-10-31" appName="OpenSkill Studio" />);
    expect(container.textContent).toContain("1000 PAIRS MILESTONE!");
    expect(container.textContent).toContain("LEGENDARY");
    expect(container.textContent).toContain("8,000");
    expect(container.textContent).toContain("webhooks");
  });
  it("shows stats", () => {
    const { container } = render(<Card pairCount={1000} commitCount={6500} backendTests={6000} frontendTests={2000} totalFiles={4000} categories={[]} achievedAt="2026-10-31" appName="App" />);
    expect(container.textContent).toContain("6,500");
    expect(container.textContent).toContain("6,000");
  });
});
