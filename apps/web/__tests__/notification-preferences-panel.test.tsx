import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { NotificationPreferencesPanel } from "@/components/notification-preferences-panel";

const prefs = { channels: { email: true, in_app: true, webhook: false, slack: false }, events: { install: true, review: true, security: true, revenue: false, update: true, uninstall: true }, quietHoursStart: 0, quietHoursEnd: 0 };

describe("NotificationPreferencesPanel", () => {
  it("renders channels and events", () => {
    const { container } = render(<NotificationPreferencesPanel prefs={prefs} />);
    expect(container.textContent).toContain("Email");
    expect(container.textContent).toContain("Installs");
    expect(container.textContent).toContain("Quiet hours");
  });
  it("toggles channel", () => {
    const fn = vi.fn();
    const { container } = render(<NotificationPreferencesPanel prefs={prefs} onChange={fn} />);
    const buttons = container.querySelectorAll("button");
    fireEvent.click(buttons[2]); // webhook
    expect(fn).toHaveBeenCalled();
  });
});
