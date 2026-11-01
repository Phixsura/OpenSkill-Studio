import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiWebhookEventFilterCard from "../src/components/api-developer-api-api-webhook-event-filter-card";

const filters = [
  { filter_id: "prod", destination: "https://a.com", include_events: ["push"], exclude_events: ["ping"], matched_count: 500, dropped_count: 50 },
];

describe("APIDeveloperAPIApiWebhookEventFilterCard", () => {
  it("shows filters", () => {
    const { container } = render(<APIDeveloperAPIApiWebhookEventFilterCard filters={filters} appName="App" />);
    expect(container.textContent).toContain("Event Filters");
    expect(container.textContent).toContain("prod");
    expect(container.textContent).toContain("500 matched");
    expect(container.textContent).toContain("50 dropped");
    expect(container.textContent).toContain("+push");
    expect(container.textContent).toContain("-ping");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiWebhookEventFilterCard filters={[]} appName="App" />);
    expect(container.textContent).toContain("No event filters");
  });
});
