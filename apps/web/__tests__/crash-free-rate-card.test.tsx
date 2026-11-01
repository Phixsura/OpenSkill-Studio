import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CrashFreeRateCard } from "@/components/crash-free-rate-card";

const mockStats = {
  crashFreeRate: 99.2,
  totalSessions: 15000,
  totalCrashes: 120,
  uniqueCrashes: 5,
  openIssues: 3,
  topCrash: { errorType: "TypeError", message: "Cannot read property 'id'", count: 45 },
};

describe("CrashFreeRateCard", () => {
  it("renders crash-free rate", () => {
    const { container } = render(<CrashFreeRateCard stats={mockStats} extensionName="Slack Bot" />);
    expect(container.textContent).toContain("99.2%");
    expect(container.textContent).toContain("Crash-Free Rate");
    expect(container.textContent).toContain("Good");
  });

  it("renders session stats", () => {
    const { container } = render(<CrashFreeRateCard stats={mockStats} extensionName="Test" />);
    expect(container.textContent).toContain("15,000");
    expect(container.textContent).toContain("120");
    expect(container.textContent).toContain("3");
  });

  it("shows top crash", () => {
    const { container } = render(<CrashFreeRateCard stats={mockStats} extensionName="Test" />);
    expect(container.textContent).toContain("TypeError");
    expect(container.textContent).toContain("45x");
  });

  it("calls onViewCrashes", () => {
    const onView = vi.fn();
    const { getByText } = render(
      <CrashFreeRateCard stats={mockStats} extensionName="Test" onViewCrashes={onView} />
    );
    fireEvent.click(getByText("View all crashes →"));
    expect(onView).toHaveBeenCalled();
  });
});
