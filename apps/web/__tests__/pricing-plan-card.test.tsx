import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PricingPlanCard } from "@/components/pricing-plan-card";

describe("PricingPlanCard", () => {
  it("renders free", () => {
    const { container } = render(
      <PricingPlanCard name="Free" priceDisplay="Free" billing="" features={["5 apps"]}
        cta="Get Started" recommended={false} popular={false} onSelect={vi.fn()} />
    );
    expect(container.textContent).toContain("Free");
    expect(container.textContent).toContain("✓");
    expect(container.textContent).toContain("5 apps");
    expect(container.textContent).toContain("Get Started");
  });
  it("renders popular", () => {
    const { container } = render(
      <PricingPlanCard name="Pro" priceDisplay="$99" billing="/mo" features={["Unlimited"]}
        cta="Start Trial" recommended={true} popular={true} onSelect={vi.fn()} />
    );
    expect(container.textContent).toContain("Most Popular");
    expect(container.textContent).toContain("$99");
    expect(container.textContent).toContain("/mo");
  });
  it("select", () => {
    const fn = vi.fn();
    const { container } = render(
      <PricingPlanCard name="X" priceDisplay="$10" billing="/mo" features={[]}
        cta="Go" recommended={false} popular={false} onSelect={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Go")!);
    expect(fn).toHaveBeenCalled();
  });
});
