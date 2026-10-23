import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SubscriptionManagementCard } from "@/components/subscription-management-card";

describe("SubscriptionManagementCard", () => {
  it("renders active", () => {
    const { container } = render(
      <SubscriptionManagementCard plan="pro" billingCycle="monthly" status="active"
        periodEnd="2026-11-23T00:00:00" cancelAtEnd={false}
        onCancel={vi.fn()} onUpgrade={vi.fn()} onResume={vi.fn()} />
    );
    expect(container.textContent).toContain("pro Plan");
    expect(container.textContent).toContain("active");
    expect(container.textContent).toContain("Renews on");
    expect(container.textContent).toContain("Cancel");
  });
  it("cancel", () => {
    const fn = vi.fn();
    const { container } = render(
      <SubscriptionManagementCard plan="pro" billingCycle="monthly" status="active"
        periodEnd="2026-11-23" cancelAtEnd={false}
        onCancel={fn} onUpgrade={vi.fn()} onResume={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Cancel")!);
    expect(fn).toHaveBeenCalled();
  });
});
