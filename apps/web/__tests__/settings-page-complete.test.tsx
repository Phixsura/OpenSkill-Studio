import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SettingsPageComplete } from "@/components/settings-page-complete";

describe("SettingsPageComplete", () => {
  const tabs = [
    { id: "general", label: "General", icon: "⚙️", active: true },
    { id: "security", label: "Security", icon: "🔒", active: false },
  ];
  it("renders settings layout", () => {
    const { container } = render(
      <SettingsPageComplete appName="SuperApp" version="2.0.0" tabs={tabs}
        activeTab="general" onTabChange={vi.fn()}>
        <p>Settings content</p>
      </SettingsPageComplete>
    );
    expect(container.textContent).toContain("SuperApp");
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("General");
    expect(container.textContent).toContain("Security");
    expect(container.textContent).toContain("Settings content");
  });
});
