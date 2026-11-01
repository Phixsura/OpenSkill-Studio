import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-webhook-signature-verifier-card";

describe("SignatureVerifierCard", () => {
  it("shows verifiers", () => {
    const verifiers = [{ consumer_id: "c1", algorithm: "sha256", valid_count: 100, invalid_count: 2 }];
    const { container } = render(<Card verifiers={verifiers} appName="App" />);
    expect(container.textContent).toContain("Signature Verifier");
    expect(container.textContent).toContain("c1");
    expect(container.textContent).toContain("sha256");
  });
  it("shows empty", () => {
    const { container } = render(<Card verifiers={[]} appName="App" />);
    expect(container.textContent).toContain("No verifiers configured");
  });
});
