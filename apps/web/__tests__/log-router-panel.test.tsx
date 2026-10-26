import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LogRouterPanel } from "@/components/log-router-panel";

const mockDests = [
  { destId: "console", name: "Console", destType: "console" as const, minLevel: "debug", enabled: true, routedCount: 5000 },
  { destId: "slack", name: "Slack Alerts", destType: "webhook" as const, minLevel: "error", enabled: true, routedCount: 120 },
  { destId: "dd", name: "Datadog", destType: "aggregator" as const, minLevel: "info", enabled: false, routedCount: 3000 },
];

describe("LogRouterPanel", () => {
  it("renders destinations", () => {
    const { container } = render(<LogRouterPanel destinations={mockDests} />);
    expect(container.textContent).toContain("Console");
    expect(container.textContent).toContain("Slack Alerts");
    expect(container.textContent).toContain("2 active");
  });

  it("shows min level and counts", () => {
    const { container } = render(<LogRouterPanel destinations={mockDests} />);
    expect(container.textContent).toContain("≥error");
    expect(container.textContent).toContain("×5000");
  });

  it("calls onToggle", () => {
    const onToggle = vi.fn();
    const { getAllByText } = render(<LogRouterPanel destinations={mockDests} onToggle={onToggle} />);
    fireEvent.click(getAllByText("Off")[0]);
    expect(onToggle).toHaveBeenCalledWith("dd");
  });

  it("calls onRemove", () => {
    const onRemove = vi.fn();
    const { container } = render(<LogRouterPanel destinations={mockDests} onRemove={onRemove} />);
    const removeBtn = container.querySelectorAll("button");
    const del = Array.from(removeBtn).find(b => b.textContent === "✕");
    if (del) fireEvent.click(del);
    expect(onRemove).toHaveBeenCalled();
  });
});
