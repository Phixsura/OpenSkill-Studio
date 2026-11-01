import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiPlatformApiWebhookEventSamplingCard from "../src/components/api-developer-platform-sdk-api-platform-api-webhook-event-sampling-card";

const samples = [
  { event_id: "e1", event_type: "push", status_code: 200, latency_ms: 50 },
  { event_id: "e2", event_type: "issue", status_code: 500, latency_ms: 120 },
];

describe("Card", () => {
  it("shows samples", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiWebhookEventSamplingCard samples={samples} totalCount={100} errorCount={5} appName="App" />);
    expect(container.textContent).toContain("Event Sampling");
    expect(container.textContent).toContain("100 sampled");
    expect(container.textContent).toContain("5 errors");
    expect(container.textContent).toContain("push");
    expect(container.textContent).toContain("500");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiWebhookEventSamplingCard samples={[]} totalCount={0} errorCount={0} appName="App" />);
    expect(container.textContent).toContain("No sampled events");
  });
});
