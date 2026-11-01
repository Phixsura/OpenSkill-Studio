import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiWebhookRoutingTableCard from "../src/components/api-developer-api-api-developer-api-webhook-routing-table-card";

const rules = [
  { rule_id: "r1", event_pattern: "order.*", destination: "https://billing.example.com", enabled: true, matches: 1500 },
  { rule_id: "r2", event_pattern: "user.*", destination: "https://crm.example.com", enabled: false, matches: 0 },
];

describe("APIDeveloperAPIApiDeveloperApiWebhookRoutingTableCard", () => {
  it("shows routing table", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiWebhookRoutingTableCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("Routing Table");
    expect(container.textContent).toContain("1/2 active");
    expect(container.textContent).toContain("order.*");
    expect(container.textContent).toContain("1500");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiWebhookRoutingTableCard rules={[]} appName="App" />);
    expect(container.textContent).toContain("No routing rules");
  });
});
