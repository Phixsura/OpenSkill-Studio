import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CostBreakdownCard } from "@/components/cost-breakdown-card";

describe("CostBreakdownCard", () => {
  it("renders costs", () => {
    const { container } = render(
      <CostBreakdownCard totalUsd={49.50} breakdown={{ api: 20, storage: 10, bandwidth: 9.5, compute: 10 }} />
    );
    expect(container.textContent).toContain("$49.50");
    expect(container.textContent).toContain("API Calls");
    expect(container.textContent).toContain("$20.00");
  });
  it("shows zero costs", () => {
    const { container } = render(
      <CostBreakdownCard totalUsd={0} breakdown={{ api: 0, storage: 0, bandwidth: 0, compute: 0 }} />
    );
    expect(container.textContent).toContain("$0.00");
  });
});
