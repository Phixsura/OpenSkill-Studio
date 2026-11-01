import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DeveloperSettingsPanel } from "@/components/developer-settings-panel";

const settings = {
  displayName: "Alice", emailNotifications: true, webhookNotifications: false,
  defaultRuntime: "node20", theme: "dark", timezone: "UTC",
  autoDeploy: false, twoFactorEnabled: true,
};

describe("DeveloperSettingsPanel", () => {
  it("renders settings", () => {
    const { container } = render(<DeveloperSettingsPanel settings={settings} />);
    expect(container.textContent).toContain("Developer Settings");
    expect(container.textContent).toContain("Email Notifications");
    expect(container.textContent).toContain("Two-Factor Auth");
  });

  it("calls onSave", () => {
    const fn = vi.fn();
    const { getByText } = render(<DeveloperSettingsPanel settings={settings} onSave={fn} />);
    fireEvent.click(getByText("Save"));
    expect(fn).toHaveBeenCalled();
  });

  it("calls onReset", () => {
    const fn = vi.fn();
    const { getByText } = render(<DeveloperSettingsPanel settings={settings} onReset={fn} />);
    fireEvent.click(getByText("Reset"));
    expect(fn).toHaveBeenCalled();
  });
});
