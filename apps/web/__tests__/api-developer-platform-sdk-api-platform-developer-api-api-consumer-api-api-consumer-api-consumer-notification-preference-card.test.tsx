import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-notification-preference-card";

describe("ConsumerNotificationPreferenceCard", () => {
  it("shows channels and muted", () => {
    const channels = [{ type: "email", target: "a@b.com", enabled: true }, { type: "slack", target: "#alerts", enabled: false }];
    const { container } = render(<Card consumerId="c1" channels={channels} mutedCategories={["billing"]} digestMode="daily" appName="App" />);
    expect(container.textContent).toContain("Notification Preferences");
    expect(container.textContent).toContain("email: a@b.com");
    expect(container.textContent).toContain("ON");
    expect(container.textContent).toContain("OFF");
    expect(container.textContent).toContain("billing");
    expect(container.textContent).toContain("daily");
  });
  it("shows empty channels", () => {
    const { container } = render(<Card consumerId="c1" channels={[]} mutedCategories={[]} digestMode="instant" appName="App" />);
    expect(container.textContent).toContain("No channels");
  });
});
