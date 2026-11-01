import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import WebhookLogCard from "../src/components/webhook-log-card";

const entries = [
  {
    log_id: "l1",
    event_type: "push",
    destination: "https://a.com",
    status_code: 200,
    success: true,
    duration_ms: 45,
  },
  {
    log_id: "l2",
    event_type: "issue",
    destination: "https://b.com",
    status_code: 500,
    success: false,
    duration_ms: 120,
  },
];

describe("WebhookLogCard", () => {
  it("renders header and stats", () => {
    const { container } = render(
      <WebhookLogCard entries={entries} successRate={80} totalCount={100} appName="App" />,
    );
    expect(container.textContent).toContain("Webhook Log");
    expect(container.textContent).toContain("100 deliveries");
    expect(container.textContent).toContain("80% success");
  });

  it("shows event types and status codes", () => {
    const { container } = render(
      <WebhookLogCard entries={entries} successRate={50} totalCount={2} appName="App" />,
    );
    expect(container.textContent).toContain("push");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("500");
  });

  it("shows duration", () => {
    const { container } = render(
      <WebhookLogCard entries={entries} successRate={50} totalCount={2} appName="App" />,
    );
    expect(container.textContent).toContain("45ms");
    expect(container.textContent).toContain("120ms");
  });

  it("shows empty state", () => {
    const { container } = render(
      <WebhookLogCard entries={[]} successRate={100} totalCount={0} appName="App" />,
    );
    expect(container.textContent).toContain("No webhook deliveries");
  });
});
