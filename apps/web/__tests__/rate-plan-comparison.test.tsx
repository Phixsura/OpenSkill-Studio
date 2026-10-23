import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RatePlanComparison } from "@/components/rate-plan-comparison";

describe("RatePlanComparison", () => {
  const comparisons = [
    { plan_name: "Pro", cost: 40 },
    { plan_name: "Starter", cost: 50 },
  ];
  it("renders", () => {
    const { container } = render(
      <RatePlanComparison comparisons={comparisons} recommended="Pro" onSelect={vi.fn()} />
    );
    expect(container.textContent).toContain("Plan Comparison");
    expect(container.textContent).toContain("Pro");
    expect(container.textContent).toContain("$40.00");
    expect(container.textContent).toContain("Best Value");
  });
  it("select", () => {
    const fn = vi.fn();
    const { container } = render(
      <RatePlanComparison comparisons={comparisons} recommended="Pro" onSelect={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Select Plan")!);
    expect(fn).toHaveBeenCalledWith("Pro");
  });
});
