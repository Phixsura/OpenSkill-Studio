import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import WebhookSignatureCard from "../src/components/webhook-signature-card";

const keys = [
  { key_id: "prod-key-1", active: true },
  { key_id: "prod-key-2", active: true },
  { key_id: "old-key", active: false },
];

describe("WebhookSignatureCard", () => {
  it("renders header and counts", () => {
    const { container } = render(<WebhookSignatureCard keys={keys} appName="App" />);
    expect(container.textContent).toContain("Webhook Signatures");
    expect(container.textContent).toContain("2 active / 3 total");
  });

  it("shows key IDs", () => {
    const { container } = render(<WebhookSignatureCard keys={keys} appName="App" />);
    expect(container.textContent).toContain("prod-key-1");
    expect(container.textContent).toContain("old-key");
  });

  it("shows status badges", () => {
    const { container } = render(<WebhookSignatureCard keys={keys} appName="App" />);
    expect(container.textContent).toContain("active");
    expect(container.textContent).toContain("inactive");
  });

  it("shows algorithm", () => {
    const { container } = render(<WebhookSignatureCard keys={keys} appName="App" />);
    expect(container.textContent).toContain("HMAC-SHA256");
  });

  it("shows empty state", () => {
    const { container } = render(<WebhookSignatureCard keys={[]} appName="App" />);
    expect(container.textContent).toContain("No signing keys");
  });
});
