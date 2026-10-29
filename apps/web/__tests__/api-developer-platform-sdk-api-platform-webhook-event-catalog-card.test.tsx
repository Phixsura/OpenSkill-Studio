import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiPlatformWebhookEventCatalogCard from "../src/components/api-developer-platform-sdk-api-platform-webhook-event-catalog-card";

const events = [{ event_type: "order.created", category: "orders", description: "Order was created", schema_version: "2.0", subscribers: 15 }];

describe("Card", () => {
  it("shows event catalog", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformWebhookEventCatalogCard events={events} categoryCounts={{ orders: 5, users: 3 }} appName="App" />);
    expect(container.textContent).toContain("Event Catalog");
    expect(container.textContent).toContain("order.created");
    expect(container.textContent).toContain("v2.0");
    expect(container.textContent).toContain("orders: 5");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformWebhookEventCatalogCard events={[]} categoryCounts={{}} appName="App" />);
    expect(container.textContent).toContain("No events in catalog");
  });
});
