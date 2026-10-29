import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-consumer-notification-preference-card";

describe("NotificationPrefCard", () => {
  it("shows preferences", () => {
    const prefs = [{ consumer_id: "c1", email: true, slack: false, webhook: true, frequency: "realtime", quiet_hours: "22-06" }];
    const { container } = render(<Card preferences={prefs} appName="App" />);
    expect(container.textContent).toContain("Notification Prefs");
    expect(container.textContent).toContain("c1");
    expect(container.textContent).toContain("realtime");
    expect(container.textContent).toContain("22-06");
  });
  it("shows empty", () => {
    const { container } = render(<Card preferences={[]} appName="App" />);
    expect(container.textContent).toContain("No preferences set");
  });
});
