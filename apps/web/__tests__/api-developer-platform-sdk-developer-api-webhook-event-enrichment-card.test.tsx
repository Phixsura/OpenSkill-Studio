import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKDeveloperApiWebhookEventEnrichmentCard from "../src/components/api-developer-platform-sdk-developer-api-webhook-event-enrichment-card";

const rules = [
  { rule_id: "r1", field_name: "source", source: "static", value: "platform", applied_count: 5000 },
  { rule_id: "r2", field_name: "consumer", source: "consumer", value: "", applied_count: 5000 },
];

describe("Card", () => {
  it("shows enrichment rules", () => {
    const { container } = render(<APIDeveloperPlatformSDKDeveloperApiWebhookEventEnrichmentCard rules={rules} totalEnrichments={10000} appName="App" />);
    expect(container.textContent).toContain("Event Enrichment");
    expect(container.textContent).toContain("10,000 applied");
    expect(container.textContent).toContain("static");
    expect(container.textContent).toContain("source");
    expect(container.textContent).toContain("5000×");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKDeveloperApiWebhookEventEnrichmentCard rules={[]} totalEnrichments={0} appName="App" />);
    expect(container.textContent).toContain("No enrichment rules");
  });
});
