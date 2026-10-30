import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-request-signing-card";

describe("ConsumerApiRequestSigningCard", () => {
  it("shows configured", () => {
    const { container } = render(<Card consumerId="c1" algorithm="sha256" headerName="X-Signature" includeBody={true} includePath={true} configured={true} appName="App" />);
    expect(container.textContent).toContain("Request Signing");
    expect(container.textContent).toContain("SHA256");
    expect(container.textContent).toContain("X-Signature");
    expect(container.textContent).toContain("Configured");
  });
  it("shows not set", () => {
    const { container } = render(<Card consumerId="c1" algorithm="" headerName="" includeBody={false} includePath={false} configured={false} appName="App" />);
    expect(container.textContent).toContain("Not Set");
  });
});
