import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { NotifPreferencesPanel } from "@/components/notif-preferences-panel";

const prefs = [
  { eventType: "deploy.success", email: true, inApp: true, push: false, webhook: false },
  { eventType: "error.critical", email: true, inApp: true, push: true, webhook: false },
];

describe("NotifPreferencesPanel", () => {
  it("renders preference table", () => {
    const { container } = render(<NotifPreferencesPanel prefs={prefs} isDnd={false} />);
    expect(container.textContent).toContain("deploy.success");
    expect(container.textContent).toContain("error.critical");
  });
  it("toggles DND", () => {
    const fn = vi.fn();
    const { getByText } = render(<NotifPreferencesPanel prefs={prefs} isDnd={false} onToggleDnd={fn} />);
    fireEvent.click(getByText("🔔 DND Off"));
    expect(fn).toHaveBeenCalled();
  });
  it("shows DND active", () => {
    const { container } = render(<NotifPreferencesPanel prefs={prefs} isDnd={true} />);
    expect(container.textContent).toContain("DND On");
  });
});
