import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-request-signing-card";

describe("RequestSigningCard", () => {
  it("shows configs", () => {
    const configs = [{ consumer_id: "c1", algorithm: "hmac-sha256", signed_headers: ["content-type"], include_body: true }];
    const { container } = render(<Card configs={configs} totalSigned={5000} appName="App" />);
    expect(container.textContent).toContain("Request Signing");
    expect(container.textContent).toContain("5,000 signed");
    expect(container.textContent).toContain("hmac-sha256");
    expect(container.textContent).toContain("+body");
  });
  it("shows empty", () => {
    const { container } = render(<Card configs={[]} totalSigned={0} appName="App" />);
    expect(container.textContent).toContain("No signing configs");
  });
});
