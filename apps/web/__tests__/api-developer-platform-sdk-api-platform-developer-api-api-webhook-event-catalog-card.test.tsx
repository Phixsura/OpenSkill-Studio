import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-webhook-event-catalog-card";

describe("EventCatalogCard", () => {
  it("shows events", () => {
    const events = [{ event_id: "e1", name: "order.created", category: "orders", deprecated: false, field_count: 5 }];
    const { container } = render(<Card events={events} categories={["orders"]} deprecatedCount={0} appName="App" />);
    expect(container.textContent).toContain("Event Catalog");
    expect(container.textContent).toContain("order.created");
    expect(container.textContent).toContain("orders");
  });
  it("shows empty", () => {
    const { container } = render(<Card events={[]} categories={[]} deprecatedCount={0} appName="App" />);
    expect(container.textContent).toContain("No events registered");
  });
});
