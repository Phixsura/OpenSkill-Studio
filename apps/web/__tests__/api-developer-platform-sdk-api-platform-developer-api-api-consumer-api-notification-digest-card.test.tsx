import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-notification-digest-card";

describe("NotificationDigestCard", () => {
  it("shows digests", () => {
    const digests = [{ digest_id: "d1", period: "2024-01-15", notification_count: 5, categories: { alert: 2, changelog: 3 } }];
    const { container } = render(<Card digests={digests} unreadCount={3} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Notification Digest");
    expect(container.textContent).toContain("3 pending");
    expect(container.textContent).toContain("5 items");
  });
  it("shows empty", () => {
    const { container } = render(<Card digests={[]} unreadCount={0} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No digests");
  });
});
