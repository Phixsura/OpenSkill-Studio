import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ExtensionSettingsPanel } from "@/components/extension-settings-panel";

const mockGroups = [
  { name: "General", icon: "⚙️", fields: [
    { key: "name", label: "Display Name", type: "text" as const, value: "My Extension", description: "Public name", required: true },
    { key: "theme", label: "Theme", type: "select" as const, value: "dark", description: "UI theme", options: ["light", "dark", "auto"] },
  ]},
  { name: "Advanced", icon: "🔧", fields: [
    { key: "debug", label: "Debug Mode", type: "toggle" as const, value: "false", description: "Enable debug logging" },
    { key: "timeout", label: "Timeout (ms)", type: "number" as const, value: "5000", description: "Request timeout" },
  ]},
];

describe("ExtensionSettingsPanel", () => {
  it("renders groups and fields", () => {
    const { container } = render(
      <ExtensionSettingsPanel groups={mockGroups} extensionName="Slack Bot" />
    );
    expect(container.textContent).toContain("Slack Bot Settings");
    expect(container.textContent).toContain("General");
    expect(container.textContent).toContain("Advanced");
    expect(container.textContent).toContain("Display Name");
  });

  it("switches groups", () => {
    const { getByText, container } = render(
      <ExtensionSettingsPanel groups={mockGroups} extensionName="Test" />
    );
    fireEvent.click(getByText("🔧 Advanced"));
    expect(container.textContent).toContain("Debug Mode");
    expect(container.textContent).toContain("Timeout");
  });

  it("calls onSave with values", () => {
    const onSave = vi.fn();
    const { getByText } = render(
      <ExtensionSettingsPanel groups={mockGroups} extensionName="Test" onSave={onSave} />
    );
    fireEvent.click(getByText("Save Settings"));
    expect(onSave).toHaveBeenCalledWith(expect.objectContaining({ name: "My Extension", theme: "dark" }));
  });
});
