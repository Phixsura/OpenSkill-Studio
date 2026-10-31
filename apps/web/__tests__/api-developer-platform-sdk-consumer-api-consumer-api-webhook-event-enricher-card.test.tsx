import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-consumer-api-webhook-event-enricher-card";

describe("WebhookEventEnricherCard", () => {
  it("shows rules", () => {
    const rules = [{ id: "r1", sourceType: "static", targetField: "source", value: "my-api" }, { id: "r2", sourceType: "computed", targetField: "size", value: "payload_size" }];
    const { container } = render(<Card webhookId="w1" rules={rules} enabled={true} enrichedCount={500} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Event Enricher");
    expect(container.textContent).toContain("static");
    expect(container.textContent).toContain("source");
    expect(container.textContent).toContain("500 payloads enriched");
  });
  it("shows empty", () => {
    const { container } = render(<Card webhookId="w1" rules={[]} enabled={false} enrichedCount={0} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No enrichment rules");
    expect(container.textContent).toContain("OFF");
  });
});
