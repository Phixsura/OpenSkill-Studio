import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { NotificationPreferencesPanel } from "@/components/notification-preferences-panel";

const mockPrefs = [
  { categoryId: "installs", email: true, inApp: true, slack: false },
  { categoryId: "reviews", email: true, inApp: true, slack: true },
  { categoryId: "security", email: true, inApp: true, slack: false },
  { categoryId: "billing", email: true, inApp: false, slack: false },
  { categoryId: "updates", email: false, inApp: true, slack: false },
  { categoryId: "support", email: true, inApp: true, slack: false },
];

describe("NotificationPreferencesPanel", () => {
  it("renders categories with channels", () => {
    const { container } = render(<NotificationPreferencesPanel preferences={mockPrefs} />);
    expect(container.textContent).toContain("Notification Preferences");
    expect(container.textContent).toContain("New Installs");
    expect(container.textContent).toContain("Security Alerts");
    expect(container.textContent).toContain("Email");
  });

  it("calls onSave with preferences", () => {
    const onSave = vi.fn();
    const { getByText } = render(
      <NotificationPreferencesPanel preferences={mockPrefs} onSave={onSave} />
    );
    fireEvent.click(getByText("Save Preferences"));
    expect(onSave).toHaveBeenCalledWith(mockPrefs);
  });

  it("shows saved confirmation", () => {
    const { getByText, container } = render(
      <NotificationPreferencesPanel preferences={mockPrefs} onSave={() => {}} />
    );
    fireEvent.click(getByText("Save Preferences"));
    expect(container.textContent).toContain("Saved!");
  });
});
