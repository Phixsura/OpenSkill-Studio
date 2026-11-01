import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIWebhookSignatureVerifierCard from "../src/components/api-developer-api-webhook-signature-verifier-card";

const stats = { total: 100, valid: 95, invalid: 5 };
const results = [
  { delivery_id: "d1", valid: true, algorithm: "sha256", reason: "" },
  { delivery_id: "d2", valid: false, algorithm: "sha256", reason: "signature mismatch" },
];

describe("APIDeveloperAPIWebhookSignatureVerifierCard", () => {
  it("shows verification stats", () => {
    const { container } = render(<APIDeveloperAPIWebhookSignatureVerifierCard stats={stats} recentResults={results} appName="App" />);
    expect(container.textContent).toContain("Signature Verifier");
    expect(container.textContent).toContain("95%");
    expect(container.textContent).toContain("100 total");
    expect(container.textContent).toContain("5 invalid");
    expect(container.textContent).toContain("signature mismatch");
  });
});
