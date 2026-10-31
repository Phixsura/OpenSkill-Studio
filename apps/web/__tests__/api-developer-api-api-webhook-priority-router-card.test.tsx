import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiWebhookPriorityRouterCard from "../src/components/api-developer-api-api-webhook-priority-router-card";

const routes = [
  { route_id: "r1", event_type: "payment.completed", priority: "critical", destination: "https://billing.com", delivered_count: 500 },
  { route_id: "r2", event_type: "user.signup", priority: "normal", destination: "https://crm.com", delivered_count: 200 },
];

describe("APIDeveloperAPIApiWebhookPriorityRouterCard", () => {
  it("shows routes", () => {
    const { container } = render(<APIDeveloperAPIApiWebhookPriorityRouterCard routes={routes} appName="App" />);
    expect(container.textContent).toContain("Priority Router");
    expect(container.textContent).toContain("payment.completed");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("500 delivered");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiWebhookPriorityRouterCard routes={[]} appName="App" />);
    expect(container.textContent).toContain("No priority routes");
  });
});
