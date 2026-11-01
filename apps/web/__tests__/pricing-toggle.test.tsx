import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PricingToggle } from "@/components/pricing-toggle";

describe("PricingToggle", () => {
  it("renders monthly", () => {
    const { container } = render(
      <PricingToggle monthlyPrice={29} annualPrice={23.2} savings={69.6}
        savingsPct={20} onBillingChange={vi.fn()} />
    );
    expect(container.textContent).toContain("$29");
    expect(container.textContent).toContain("Monthly");
    expect(container.textContent).toContain("Annual");
    expect(container.textContent).toContain("Save 20%");
  });
  it("toggles to annual", () => {
    const fn = vi.fn();
    const { container } = render(
      <PricingToggle monthlyPrice={29} annualPrice={23.2} savings={69.6}
        savingsPct={20} onBillingChange={fn} />
    );
    // Find toggle button (the one with rounded-full and w-14)
    const toggleBtn = Array.from(container.querySelectorAll("button")).find(b => b.className.includes("w-14"));
    if (toggleBtn) fireEvent.click(toggleBtn);
    expect(fn).toHaveBeenCalledWith(true);
  });
});
