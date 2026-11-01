import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ExtensionComparisonTable } from "@/components/extension-comparison-table";

const mockExts = [
  { id: "e1", name: "Slack Bot", icon: "💬", version: "2.0", rating: 4.8, downloads: 15000, price: "$9.99/mo",
    features: { webhooks: true, scheduling: true, analytics: false, custom_ui: "Basic" } },
  { id: "e2", name: "Teams Bot", icon: "👥", version: "1.5", rating: 4.2, downloads: 8000, price: "Free",
    features: { webhooks: true, scheduling: false, analytics: true, custom_ui: "Advanced" } },
];

const featureLabels = [
  { key: "webhooks", label: "Webhooks" },
  { key: "scheduling", label: "Scheduling" },
  { key: "analytics", label: "Analytics" },
  { key: "custom_ui", label: "Custom UI" },
];

describe("ExtensionComparisonTable", () => {
  it("renders extensions and features", () => {
    const { container } = render(
      <ExtensionComparisonTable extensions={mockExts} featureLabels={featureLabels} />
    );
    expect(container.textContent).toContain("Compare Extensions");
    expect(container.textContent).toContain("Slack Bot");
    expect(container.textContent).toContain("Teams Bot");
    expect(container.textContent).toContain("Webhooks");
    expect(container.textContent).toContain("$9.99/mo");
  });

  it("shows check/dash for boolean features", () => {
    const { container } = render(
      <ExtensionComparisonTable extensions={mockExts} featureLabels={featureLabels} />
    );
    expect(container.textContent).toContain("✅");
    expect(container.textContent).toContain("—");
  });

  it("shows string feature values", () => {
    const { container } = render(
      <ExtensionComparisonTable extensions={mockExts} featureLabels={featureLabels} />
    );
    expect(container.textContent).toContain("Basic");
    expect(container.textContent).toContain("Advanced");
  });

  it("calls onSelect", () => {
    const onSelect = vi.fn();
    const { getAllByText } = render(
      <ExtensionComparisonTable extensions={mockExts} featureLabels={featureLabels} onSelect={onSelect} />
    );
    fireEvent.click(getAllByText("Select")[0]);
    expect(onSelect).toHaveBeenCalledWith("e1");
  });
});
