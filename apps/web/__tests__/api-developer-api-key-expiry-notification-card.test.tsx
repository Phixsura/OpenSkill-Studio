import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIKeyExpiryNotificationCard from "../src/components/api-developer-api-key-expiry-notification-card";

const notifs = [
  { notification_id: "n1", key_id: "k1", developer_id: "alice", days_until_expiry: 3, sent: false },
  { notification_id: "n2", key_id: "k2", developer_id: "bob", days_until_expiry: 30, sent: false },
];

describe("APIDeveloperAPIKeyExpiryNotificationCard", () => {
  it("shows alerts with urgent", () => {
    const { container } = render(<APIDeveloperAPIKeyExpiryNotificationCard notifications={notifs} appName="App" />);
    expect(container.textContent).toContain("Key Expiry Alerts");
    expect(container.textContent).toContain("1 urgent");
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("3d");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIKeyExpiryNotificationCard notifications={[]} appName="App" />);
    expect(container.textContent).toContain("No expiry alerts");
  });
});
