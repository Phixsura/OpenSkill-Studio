import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformSummaryCard } from "@/components/platform-summary-card";

const mockSummary = {
  totalExtensions: 500, totalDevelopers: 2000, totalInstalls: 100000,
  totalServices: 500, testsGreen: 2500, healthScore: 99.9,
};

describe("PlatformSummaryCard", () => {
  it("renders platform overview", () => {
    const { container } = render(<PlatformSummaryCard summary={mockSummary} />);
    expect(container.textContent).toContain("OpenSkill Developer Platform");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("2,500");
    expect(container.textContent).toContain("99.9%");
  });
});
