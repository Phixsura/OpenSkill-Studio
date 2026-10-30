import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-webhook-idempotency-card";

describe("WebhookIdempotencyCard", () => {
  it("shows stats", () => {
    const { container } = render(<Card newCount={9500} duplicateCount={500} duplicateRate={5} retentionHours={24} appName="App" />);
    expect(container.textContent).toContain("Webhook Idempotency");
    expect(container.textContent).toContain("9,500");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("5% duplicates");
    expect(container.textContent).toContain("24h retention");
  });
  it("shows zero", () => {
    const { container } = render(<Card newCount={0} duplicateCount={0} duplicateRate={0} retentionHours={24} appName="App" />);
    expect(container.textContent).toContain("0% duplicates");
  });
});
