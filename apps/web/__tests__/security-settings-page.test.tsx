import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SecuritySettingsPage } from "@/components/security-settings-page";

describe("SecuritySettingsPage", () => {
  const settings = [
    { key: "two_factor", label: "Two-Factor", icon: "🔐", description: "Require 2FA",
      enabled: true, type: "toggle" },
    { key: "timeout", label: "Timeout", icon: "⏰", description: "Auto-logout",
      value: 30, type: "number", unit: "minutes" },
  ];
  it("renders security settings", () => {
    const { container } = render(
      <SecuritySettingsPage settings={settings} securityScore={80} grade="A" onToggle={vi.fn()} />
    );
    expect(container.textContent).toContain("Security Settings");
    expect(container.textContent).toContain("Two-Factor");
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("80%");
    expect(container.textContent).toContain("30 minutes");
  });
});
