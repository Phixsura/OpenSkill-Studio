import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import WebhookFilterCard from "../src/components/webhook-filter-card";

const rules = [
  {
    rule_id: "r1",
    event_type: "issue.created",
    action: "include" as const,
    field: null,
    operator: "eq",
    value: null,
    priority: 10,
  },
  {
    rule_id: "r2",
    event_type: "*",
    action: "exclude" as const,
    field: "data.status",
    operator: "eq",
    value: "draft",
    priority: 1,
  },
];

describe("WebhookFilterCard", () => {
  it("renders header and counts", () => {
    const { container } = render(<WebhookFilterCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("Webhook Filters");
    expect(container.textContent).toContain("1 include");
    expect(container.textContent).toContain("1 exclude");
  });

  it("shows action badges and event types", () => {
    const { container } = render(<WebhookFilterCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("include");
    expect(container.textContent).toContain("exclude");
    expect(container.textContent).toContain("issue.created");
  });

  it("shows field conditions", () => {
    const { container } = render(<WebhookFilterCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("data.status");
    expect(container.textContent).toContain("draft");
  });

  it("shows priority", () => {
    const { container } = render(<WebhookFilterCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("P10");
    expect(container.textContent).toContain("P1");
  });

  it("shows empty state", () => {
    const { container } = render(<WebhookFilterCard rules={[]} appName="App" />);
    expect(container.textContent).toContain("No filter rules");
  });
});
