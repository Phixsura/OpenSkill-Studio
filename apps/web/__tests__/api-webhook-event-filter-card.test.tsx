import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIWebhookEventFilterCard from "../src/components/api-webhook-event-filter-card";

const filters = [{ filter_id: "f1", event_type: "push", field_path: "data.branch", operator: "eq", value: "main", enabled: true }];

describe("APIWebhookEventFilterCard", () => {
  it("shows filters", () => {
    const { container } = render(<APIWebhookEventFilterCard filters={filters} appName="App" />);
    expect(container.textContent).toContain("Event Filters");
    expect(container.textContent).toContain("data.branch eq main");
    expect(container.textContent).toContain("push");
  });
  it("shows empty", () => {
    const { container } = render(<APIWebhookEventFilterCard filters={[]} appName="App" />);
    expect(container.textContent).toContain("No event filters");
  });
});
