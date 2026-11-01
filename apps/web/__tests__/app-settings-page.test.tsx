import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppSettingsPage } from "@/components/app-settings-page";

describe("AppSettingsPage", () => {
  const sections = [
    { id: "general", label: "General", icon: "⚙️", fields: [
      { key: "name", label: "App Name", type: "text", value: "SuperApp", required: true },
    ]},
    { id: "danger", label: "Danger Zone", icon: "⚠️", fields: [
      { key: "delete", label: "Delete App", type: "action_danger", value: null },
    ]},
  ];
  it("renders settings", () => {
    const { container } = render(<AppSettingsPage sections={sections} appName="SuperApp" onSave={vi.fn()} />);
    expect(container.textContent).toContain("SuperApp Settings");
    expect(container.textContent).toContain("General");
    expect(container.textContent).toContain("Danger Zone");
    expect(container.textContent).toContain("Delete App");
    expect(container.textContent).toContain("Save Settings");
  });
});
