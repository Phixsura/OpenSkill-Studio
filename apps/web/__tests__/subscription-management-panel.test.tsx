import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SubscriptionManagementPanel } from "@/components/subscription-management-panel";

const mockSubs = [
  { id: "s1", extensionName: "Slack Bot Pro", extensionIcon: "💬", planName: "Pro", price: 999, currency: "USD", period: "month",
    status: "active" as const, currentPeriodEnd: "Nov 1, 2026", usageThisMonth: 8500, usageLimit: 10000 },
  { id: "s2", extensionName: "Analytics Plus", extensionIcon: "📊", planName: "Trial", price: 0, currency: "USD", period: "month",
    status: "trial" as const, currentPeriodEnd: "Nov 15, 2026", usageThisMonth: 200, usageLimit: 1000 },
];

describe("SubscriptionManagementPanel", () => {
  it("renders subscriptions with total", () => {
    const { container } = render(<SubscriptionManagementPanel subscriptions={mockSubs} />);
    expect(container.textContent).toContain("Subscriptions");
    expect(container.textContent).toContain("Slack Bot Pro");
    expect(container.textContent).toContain("$9.99");
  });

  it("shows usage bar", () => {
    const { container } = render(<SubscriptionManagementPanel subscriptions={mockSubs} />);
    expect(container.textContent).toContain("8,500");
    expect(container.textContent).toContain("85%");
  });

  it("calls onCancel for active sub", () => {
    const onCancel = vi.fn();
    const { getByText } = render(<SubscriptionManagementPanel subscriptions={mockSubs} onCancel={onCancel} />);
    fireEvent.click(getByText("Cancel"));
    expect(onCancel).toHaveBeenCalledWith("s1");
  });
});
