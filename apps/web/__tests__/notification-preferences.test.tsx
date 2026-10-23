import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { NotificationPreferences } from "@/components/notification-preferences";

describe("NotificationPreferences", () => {
  const events = [{ id: "app_installed", label: "App Installed", category: "Apps", channels: { email: true, push: false } }];
  const channels = [{ label: "Email", icon: "📧" }, { label: "Push", icon: "📱" }];
  it("renders preferences", () => {
    const { container } = render(
      <NotificationPreferences events={events} channels={channels} categories={["Apps"]} onToggle={vi.fn()} />
    );
    expect(container.textContent).toContain("Notification Preferences");
    expect(container.textContent).toContain("App Installed");
    expect(container.textContent).toContain("📧");
  });
});
