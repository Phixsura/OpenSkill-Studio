import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { NotificationChannelManager } from "@/components/notification-channel-manager";

const mockChannels = [
  { id: "c1", name: "Email Alerts", type: "email" as const, enabled: true,
    minSeverity: "error" as const, eventFilters: ["deploy", "crash"],
    deliveredCount: 42, failedCount: 2 },
  { id: "c2", name: "Slack", type: "slack" as const, enabled: false,
    minSeverity: "info" as const, eventFilters: [],
    deliveredCount: 100, failedCount: 0 },
];

describe("NotificationChannelManager", () => {
  it("renders channels with counts", () => {
    const { container } = render(
      <NotificationChannelManager channels={mockChannels} extensionName="MyExt" />
    );
    expect(container.textContent).toContain("MyExt");
    expect(container.textContent).toContain("Email Alerts");
    expect(container.textContent).toContain("1/2 active");
  });

  it("shows event filters", () => {
    const { container } = render(
      <NotificationChannelManager channels={mockChannels} extensionName="Test" />
    );
    expect(container.textContent).toContain("deploy");
    expect(container.textContent).toContain("crash");
  });

  it("calls onToggle", () => {
    const onToggle = vi.fn();
    const { getAllByText } = render(
      <NotificationChannelManager channels={mockChannels} extensionName="Test" onToggle={onToggle} />
    );
    fireEvent.click(getAllByText("Off")[0]);
    expect(onToggle).toHaveBeenCalledWith("c2");
  });

  it("shows failed count in red", () => {
    const { container } = render(
      <NotificationChannelManager channels={mockChannels} extensionName="Test" />
    );
    expect(container.textContent).toContain("✗ 2");
  });
});
