import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { NotificationPrefsPage } from "@/components/notification-prefs-page";

describe("NotificationPrefsPage", () => {
  it("renders prefs", () => {
    const { container } = render(
      <NotificationPrefsPage channels={["email", "slack"]} onToggle={vi.fn()}
        categories={[
          { id: "security", label: "Security", icon: "🔒", editable: false,
            channels: { email: true, slack: true } },
          { id: "deploys", label: "Deploys", icon: "🚀", editable: true,
            channels: { email: true, slack: false } },
        ]} />
    );
    expect(container.textContent).toContain("Notification Preferences");
    expect(container.textContent).toContain("Security");
    expect(container.textContent).toContain("required");
    expect(container.textContent).toContain("Deploys");
  });
});
