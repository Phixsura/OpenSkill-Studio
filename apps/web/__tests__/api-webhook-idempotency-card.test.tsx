import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIWebhookIdempotencyCard from "../src/components/api-webhook-idempotency-card";

describe("APIWebhookIdempotencyCard", () => {
  it("shows stats", () => {
    const { container } = render(<APIWebhookIdempotencyCard stats={{ total_keys: 1000, duplicates_prevented: 50, delivered: 950 }} appName="App" />);
    expect(container.textContent).toContain("Webhook Idempotency");
    expect(container.textContent).toContain("1000");
    expect(container.textContent).toContain("950");
    expect(container.textContent).toContain("50");
  });
});
