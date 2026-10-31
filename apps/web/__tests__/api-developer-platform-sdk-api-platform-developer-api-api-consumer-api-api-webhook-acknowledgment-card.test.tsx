import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-webhook-acknowledgment-card";

describe("WebhookAcknowledgmentCard", () => {
  it("shows ack stats", () => {
    const { container } = render(<Card ackRate={98.5} avgLatencyMs={250} unackedCount={3} totalDeliveries={10000} appName="App" />);
    expect(container.textContent).toContain("Webhook Acks");
    expect(container.textContent).toContain("98.5%");
    expect(container.textContent).toContain("250ms");
    expect(container.textContent).toContain("3 unacked");
  });
  it("no unacked badge when zero", () => {
    const { container } = render(<Card ackRate={100} avgLatencyMs={100} unackedCount={0} totalDeliveries={500} appName="App" />);
    expect(container.textContent).not.toContain("unacked");
  });
});
