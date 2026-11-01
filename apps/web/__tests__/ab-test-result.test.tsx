import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AbTestResult } from "@/components/ab-test-result";

describe("AbTestResult", () => {
  it("renders significant", () => {
    const { container } = render(
      <AbTestResult controlRate={5} variantRate={6} liftPct={20}
        zScore={2.5} significant={true} winner="variant" confidence="95%" />
    );
    expect(container.textContent).toContain("A/B Test Result");
    expect(container.textContent).toContain("variant");
    expect(container.textContent).toContain("95%");
    expect(container.textContent).toContain("5%");
    expect(container.textContent).toContain("6%");
    expect(container.textContent).toContain("+20%");
    expect(container.textContent).toContain("Statistically significant");
  });
});
