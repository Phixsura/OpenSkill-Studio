import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APINotificationPreferenceCard from "../src/components/api-notification-preference-card";

const prefs = [
  { user_id: "alice", channels: ["email", "slack"], muted_count: 2, has_quiet_hours: true },
  { user_id: "bob", channels: ["email"], muted_count: 0, has_quiet_hours: false },
];

describe("APINotificationPreferenceCard", () => {
  it("renders header and user count", () => {
    const { container } = render(<APINotificationPreferenceCard preferences={prefs} appName="App" />);
    expect(container.textContent).toContain("Notification Prefs");
    expect(container.textContent).toContain("2 users");
  });

  it("shows channels and muted count", () => {
    const { container } = render(<APINotificationPreferenceCard preferences={prefs} appName="App" />);
    expect(container.textContent).toContain("email");
    expect(container.textContent).toContain("slack");
    expect(container.textContent).toContain("2 muted");
    expect(container.textContent).toContain("quiet hours");
  });

  it("shows empty state", () => {
    const { container } = render(<APINotificationPreferenceCard preferences={[]} appName="App" />);
    expect(container.textContent).toContain("No custom preferences");
  });
});
