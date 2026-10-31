import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiWebhookConsumerPreferenceManagerCard from "../src/components/api-developer-platform-sdk-api-webhook-consumer-preference-manager-card";

const prefs = [{ consumer_id: "acme", max_retries: 5, timeout_ms: 10000, content_type: "application/json", signature_algorithm: "sha256", batch_enabled: true }];

describe("Card", () => {
  it("shows preferences", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiWebhookConsumerPreferenceManagerCard preferences={prefs} batchCount={1} appName="App" />);
    expect(container.textContent).toContain("Consumer Delivery Settings");
    expect(container.textContent).toContain("acme");
    expect(container.textContent).toContain("5 retries");
    expect(container.textContent).toContain("10000ms");
    expect(container.textContent).toContain("batch");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiWebhookConsumerPreferenceManagerCard preferences={[]} batchCount={0} appName="App" />);
    expect(container.textContent).toContain("No custom preferences");
  });
});
