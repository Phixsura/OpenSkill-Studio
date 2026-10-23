import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AbTestResultsCard } from "@/components/ab-test-results-card";

describe("AbTestResultsCard", () => {
  it("renders", () => {
    const { container } = render(
      <AbTestResultsCard control={{ rate: 4, visitors: 5000, conversions: 200 }}
        variant={{ rate: 6, visitors: 5000, conversions: 300 }} liftPct={50}
        winner="variant" significant={true} recommendation="Promote variant"
        onPromote={vi.fn()} />
    );
    expect(container.textContent).toContain("A/B Test Results");
    expect(container.textContent).toContain("4%");
    expect(container.textContent).toContain("6%");
    expect(container.textContent).toContain("🏆");
    expect(container.textContent).toContain("↑ 50%");
    expect(container.textContent).toContain("Statistically significant");
    expect(container.textContent).toContain("Promote Variant");
  });
  it("promote", () => {
    const fn = vi.fn();
    const { container } = render(
      <AbTestResultsCard control={{ rate: 4, visitors: 5000, conversions: 200 }}
        variant={{ rate: 6, visitors: 5000, conversions: 300 }} liftPct={50}
        winner="variant" significant={true} recommendation="Promote" onPromote={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Promote Variant")!);
    expect(fn).toHaveBeenCalled();
  });
});
