import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-mutual-tls-card";

describe("MutualTlsCard", () => {
  it("shows certs", () => {
    const certs = [{ cert_id: "c1", consumer_id: "c1", subject_cn: "api.client.com", status: "active", fingerprint_short: "ab12...ef56" }];
    const { container } = render(<Card certs={certs} activeCertCount={1} appName="App" />);
    expect(container.textContent).toContain("Mutual TLS");
    expect(container.textContent).toContain("api.client.com");
    expect(container.textContent).toContain("1 active");
  });
  it("shows empty", () => {
    const { container } = render(<Card certs={[]} activeCertCount={0} appName="App" />);
    expect(container.textContent).toContain("No mTLS certificates");
  });
});
