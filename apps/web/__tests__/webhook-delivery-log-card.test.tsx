import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import WebhookDeliveryLogCard from "../src/components/webhook-delivery-log-card";

const attempts = [
  {
    attempt_id: "a1",
    event_type: "user.created",
    url: "https://hooks.example.com/wh",
    status_code: 200,
    success: true,
    response_time_ms: 45,
    attempt_number: 1,
    error: "",
    timestamp: new Date(Date.now() - 60_000).toISOString(),
  },
  {
    attempt_id: "a2",
    event_type: "order.placed",
    url: "https://hooks.example.com/wh",
    status_code: 500,
    success: false,
    response_time_ms: 120,
    attempt_number: 2,
    error: "server error",
    timestamp: new Date(Date.now() - 300_000).toISOString(),
  },
];

describe("WebhookDeliveryLogCard", () => {
  it("renders header and app name", () => {
    const { container } = render(
      <WebhookDeliveryLogCard
        attempts={attempts}
        successRate={95.5}
        avgResponseMs={82}
        appName="My App"
      />,
    );
    expect(container.textContent).toContain("Webhook Deliveries");
    expect(container.textContent).toContain("My App");
  });

  it("shows success rate", () => {
    const { container } = render(
      <WebhookDeliveryLogCard
        attempts={attempts}
        successRate={95.5}
        avgResponseMs={82}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("95.5% success");
  });

  it("shows avg response time", () => {
    const { container } = render(
      <WebhookDeliveryLogCard
        attempts={attempts}
        successRate={95}
        avgResponseMs={82}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("avg 82ms");
  });

  it("renders event types", () => {
    const { container } = render(
      <WebhookDeliveryLogCard
        attempts={attempts}
        successRate={95}
        avgResponseMs={0}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("user.created");
    expect(container.textContent).toContain("order.placed");
  });

  it("shows status codes", () => {
    const { container } = render(
      <WebhookDeliveryLogCard
        attempts={attempts}
        successRate={95}
        avgResponseMs={0}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("500");
  });

  it("shows retry number", () => {
    const { container } = render(
      <WebhookDeliveryLogCard
        attempts={attempts}
        successRate={95}
        avgResponseMs={0}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("retry #2");
  });

  it("shows empty state", () => {
    const { container } = render(
      <WebhookDeliveryLogCard attempts={[]} successRate={100} avgResponseMs={0} appName="App" />,
    );
    expect(container.textContent).toContain("No deliveries");
  });
});
