import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PricingToggle } from "@/components/pricing-toggle";

describe("PricingToggle", () => {
  it("shows monthly active", () => {
    const { container } = render(<PricingToggle interval="monthly" onToggle={vi.fn()} />);
    expect(container.textContent).toContain("Monthly");
    expect(container.textContent).toContain("Yearly");
  });
  it("shows savings", () => {
    const { container } = render(<PricingToggle interval="yearly" onToggle={vi.fn()} savingsPct={17} />);
    expect(container.textContent).toContain("Save 17%");
  });
  it("toggles", () => {
    const fn = vi.fn();
    const { container } = render(<PricingToggle interval="monthly" onToggle={fn} />);
    fireEvent.click(container.querySelector("button[role='switch']")!);
    expect(fn).toHaveBeenCalledWith("yearly");
  });
});
