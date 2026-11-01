import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import WebhookSigVerifierCard from "../src/components/api-developer-platform-sdk-consumer-api-webhook-sig-verifier-card";

describe("WebhookSigVerifierCard", () => {
  it("renders title and webhooks", () => {
    const { container } = render(<WebhookSigVerifierCard />);
    expect(container.textContent).toContain("Signature Verifier");
    expect(container.textContent).toContain("wh-orders");
    expect(container.textContent).toContain("wh-payments");
  });

  it("shows algorithm and active count", () => {
    const { container } = render(<WebhookSigVerifierCard />);
    expect(container.textContent).toContain("sha256");
    expect(container.textContent).toContain("sha512");
    expect(container.textContent).toContain("2 active webhooks");
  });
});
