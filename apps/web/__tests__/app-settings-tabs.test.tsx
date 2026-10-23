import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppSettingsTabs } from "@/components/app-settings-tabs";

describe("AppSettingsTabs", () => {
  const tabs = [
    { key: "general", title: "General", icon: "⚙️" },
    { key: "api_keys", title: "API Keys (2)", icon: "🔑" },
    { key: "danger", title: "Danger Zone", icon: "⚠️" },
  ];
  it("renders tabs", () => {
    const { container } = render(
      <AppSettingsTabs tabs={tabs}><p>Content</p></AppSettingsTabs>
    );
    expect(container.textContent).toContain("General");
    expect(container.textContent).toContain("API Keys (2)");
    expect(container.textContent).toContain("Danger Zone");
    expect(container.textContent).toContain("Content");
  });
  it("switches tab", () => {
    const { container } = render(
      <AppSettingsTabs tabs={tabs}><p>Tab content</p></AppSettingsTabs>
    );
    fireEvent.click(container.querySelectorAll("button")[1]);
    // Verify the button is now active (has blue class)
    const btn = container.querySelectorAll("button")[1];
    expect(btn.className).toContain("blue");
  });
});
