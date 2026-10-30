import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-mutual-tls-card";

describe("ConsumerApiMutualTlsCard", () => {
  it("shows certs", () => {
    const certs = [{ id: "c1", cn: "api.example.com", fingerprint: "a".repeat(64), issuer: "LetsEncrypt", expiresAt: "2027-06-01", revoked: false }];
    const { container } = render(<Card certs={certs} consumerId="c1" mtlsRequired={true} appName="App" />);
    expect(container.textContent).toContain("Mutual TLS");
    expect(container.textContent).toContain("api.example.com");
    expect(container.textContent).toContain("Required");
    expect(container.textContent).toContain("LetsEncrypt");
  });
  it("shows empty", () => {
    const { container } = render(<Card certs={[]} consumerId="c1" mtlsRequired={false} appName="App" />);
    expect(container.textContent).toContain("No certificates");
    expect(container.textContent).toContain("Optional");
  });
});
