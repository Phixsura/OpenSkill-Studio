import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiConsumerWebhookPreferenceCard from "../src/components/api-developer-platform-sdk-api-consumer-webhook-preference-card";

const prefs = [{ consumer_id: "acme", preferred_format: "json", compression: "gzip", batch_enabled: true }];

describe("Card", () => {
  it("shows preferences", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiConsumerWebhookPreferenceCard preferences={prefs} formatDistribution={{ json: 8, xml: 2 }} batchCount={3} appName="App" />);
    expect(container.textContent).toContain("Webhook Preferences");
    expect(container.textContent).toContain("3 batch enabled");
    expect(container.textContent).toContain("json: 8");
    expect(container.textContent).toContain("acme");
    expect(container.textContent).toContain("gzip");
    expect(container.textContent).toContain("batch");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiConsumerWebhookPreferenceCard preferences={[]} formatDistribution={{}} batchCount={0} appName="App" />);
    expect(container.textContent).toContain("No preferences set");
  });
});
