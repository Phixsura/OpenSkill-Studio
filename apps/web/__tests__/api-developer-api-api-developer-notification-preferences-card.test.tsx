import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperNotificationPreferencesCard from "../src/components/api-developer-api-api-developer-notification-preferences-card";

const pref = { developer_id: "dev1", enabled_channels: ["email", "slack"], enabled_categories: ["incident", "security"], quiet_hours_start: 22, quiet_hours_end: 8 };

describe("APIDeveloperAPIApiDeveloperNotificationPreferencesCard", () => {
  it("shows preferences", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperNotificationPreferencesCard preference={pref} appName="App" />);
    expect(container.textContent).toContain("Notification Preferences");
    expect(container.textContent).toContain("dev1");
    expect(container.textContent).toContain("email");
    expect(container.textContent).toContain("slack");
    expect(container.textContent).toContain("incident");
    expect(container.textContent).toContain("22:00");
  });
});
