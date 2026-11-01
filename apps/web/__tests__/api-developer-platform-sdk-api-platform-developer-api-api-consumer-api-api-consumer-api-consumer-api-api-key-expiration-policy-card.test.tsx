import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-key-expiration-policy-card";

describe("ConsumerApiKeyExpirationPolicyCard", () => {
  it("shows keys", () => {
    const keys = [{ id: "k1", status: "warning", daysRemaining: 10, expiresAt: "2026-09-01" }];
    const { container } = render(<Card keys={keys} maxLifetimeDays={90} warnBeforeDays={14} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Key Expiration Policy");
    expect(container.textContent).toContain("k1");
    expect(container.textContent).toContain("10d left");
    expect(container.textContent).toContain("warning");
    expect(container.textContent).toContain("Max: 90d");
  });
  it("shows empty", () => {
    const { container } = render(<Card keys={[]} maxLifetimeDays={365} warnBeforeDays={30} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No keys tracked");
  });
});
