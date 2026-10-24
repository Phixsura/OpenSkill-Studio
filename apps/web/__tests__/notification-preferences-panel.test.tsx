import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { NotificationPreferencesPanel } from "@/components/notification-preferences-panel";

describe("NotificationPreferencesPanel", () => {
  const categories = [
    { key: "updates", label: "Updates", description: "App updates" },
    { key: "security", label: "Security", description: "Alerts", locked: true },
  ];
  const channels = ["email", "push"];
  const prefs = { updates: { email: true, push: false }, security: { email: true, push: true } };

  it("renders table", () => {
    const { container } = render(
      <NotificationPreferencesPanel categories={categories} channels={channels} preferences={prefs} onToggle={vi.fn()} />
    );
    expect(container.textContent).toContain("Notification Preferences");
    expect(container.textContent).toContain("Updates");
    expect(container.textContent).toContain("Security");
    const checkboxes = container.querySelectorAll("input[type='checkbox']");
    expect(checkboxes.length).toBe(4);
  });

  it("toggle fires callback", () => {
    const fn = vi.fn();
    const { container } = render(
      <NotificationPreferencesPanel categories={categories} channels={channels} preferences={prefs} onToggle={fn} />
    );
    const checkboxes = container.querySelectorAll("input[type='checkbox']");
    fireEvent.click(checkboxes[0]);
    expect(fn).toHaveBeenCalledWith("updates", "email", false);
  });
});
