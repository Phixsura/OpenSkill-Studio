import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AbTestResultsCard } from "@/components/ab-test-results-card";

describe("AbTestResultsCard", () => {
  it("renders results", () => {
    const { container } = render(
      <AbTestResultsCard experimentName="Button Color" winner="B" bestRate={8.0}
        results={[
          { name: "A", views: 1000, conversions: 50, rate: 5.0 },
          { name: "B", views: 1000, conversions: 80, rate: 8.0 },
        ]} />
    );
    expect(container.textContent).toContain("Button Color");
    expect(container.textContent).toContain("Winner: B");
    expect(container.textContent).toContain("8%");
    expect(container.textContent).toContain("1,000 views");
    expect(container.textContent).toContain("🏆");
  });
});
