import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiPlatformApiDeveloperApiKeyExpiryMonitorCard from "../src/components/api-developer-platform-sdk-api-platform-api-developer-api-key-expiry-monitor-card";

const keys = [
  { key_id: "k1", consumer_id: "acme", days_until_expiry: 5, urgency: "critical", expired: false },
  { key_id: "k2", consumer_id: "beta", days_until_expiry: 0, urgency: "expired", expired: true },
];

describe("Card", () => {
  it("shows key expiry", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiDeveloperApiKeyExpiryMonitorCard keys={keys} expiringCount={1} expiredCount={1} appName="App" />);
    expect(container.textContent).toContain("Key Expiry Monitor");
    expect(container.textContent).toContain("1 expired");
    expect(container.textContent).toContain("1 expiring");
    expect(container.textContent).toContain("5d");
    expect(container.textContent).toContain("EXPIRED");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiDeveloperApiKeyExpiryMonitorCard keys={[]} expiringCount={0} expiredCount={0} appName="App" />);
    expect(container.textContent).toContain("No key expiry data");
  });
});
