import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import WebhookEndpointCard from "../src/components/webhook-endpoint-card";

const endpoints = [
  {
    endpoint_id: "ep1",
    url: "https://hooks.example.com/a",
    events: ["push", "issue"],
    enabled: true,
    success_rate: 99.5,
    total_deliveries: 500,
  },
  {
    endpoint_id: "ep2",
    url: "https://hooks.example.com/b",
    events: ["push"],
    enabled: false,
    success_rate: 100,
    total_deliveries: 0,
  },
];

describe("WebhookEndpointCard", () => {
  it("renders header and enabled count", () => {
    const { container } = render(<WebhookEndpointCard endpoints={endpoints} appName="App" />);
    expect(container.textContent).toContain("Webhook Endpoints");
    expect(container.textContent).toContain("1/2 enabled");
  });

  it("shows URLs and events", () => {
    const { container } = render(<WebhookEndpointCard endpoints={endpoints} appName="App" />);
    expect(container.textContent).toContain("hooks.example.com");
    expect(container.textContent).toContain("push");
    expect(container.textContent).toContain("issue");
  });

  it("shows success rates", () => {
    const { container } = render(<WebhookEndpointCard endpoints={endpoints} appName="App" />);
    expect(container.textContent).toContain("99.5%");
  });

  it("shows empty state", () => {
    const { container } = render(<WebhookEndpointCard endpoints={[]} appName="App" />);
    expect(container.textContent).toContain("No webhook endpoints");
  });
});
