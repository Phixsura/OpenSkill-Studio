import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { BundlePricingCard } from "@/components/bundle-pricing-card";

describe("BundlePricingCard", () => {
  it("renders", () => {
    const apps = [{ id: "a1", name: "App A", price: 10 }, { id: "a2", name: "App B", price: 20 }];
    const fn = vi.fn();
    const { container } = render(
      <BundlePricingCard name="Starter" apps={apps} bundlePrice={22.5} individualTotal={30}
        savings={7.5} discountPct={25} onBuy={fn} />
    );
    expect(container.textContent).toContain("Starter");
    expect(container.textContent).toContain("SAVE 25%");
    expect(container.textContent).toContain("$22.50");
    expect(container.textContent).toContain("-$7.50");
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Buy Bundle")!);
    expect(fn).toHaveBeenCalled();
  });
});
