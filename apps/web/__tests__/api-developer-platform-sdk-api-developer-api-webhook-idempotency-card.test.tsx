import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperApiWebhookIdempotencyCard from "../src/components/api-developer-platform-sdk-api-developer-api-webhook-idempotency-card";

describe("Card", () => {
  it("shows idempotency stats", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiWebhookIdempotencyCard activeKeys={5000} duplicatesBlocked={1200} appName="App" />);
    expect(container.textContent).toContain("Webhook Idempotency");
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("1,200");
    expect(container.textContent).toContain("Active Keys");
    expect(container.textContent).toContain("Duplicates Blocked");
  });
});
