import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { NotificationPrefsPanel } from "@/components/notification-prefs-panel";

describe("NotificationPrefsPanel", () => {
  it("renders and toggles", () => {
    const onToggle = vi.fn();
    const { container, getAllByRole } = render(
      <NotificationPrefsPanel
        channels={["email", "push"]}
        categories={["security", "billing"]}
        prefs={{ security: { email: true, push: true }, billing: { email: true, push: false } }}
        onToggle={onToggle} />
    );
    expect(container.textContent).toContain("Notification Preferences");
    expect(container.textContent).toContain("security");
    expect(container.textContent).toContain("billing");
    const buttons = getAllByRole("button");
    fireEvent.click(buttons[0]); // toggle security email off
    expect(onToggle).toHaveBeenCalledWith("security", "email", false);
  });
});
