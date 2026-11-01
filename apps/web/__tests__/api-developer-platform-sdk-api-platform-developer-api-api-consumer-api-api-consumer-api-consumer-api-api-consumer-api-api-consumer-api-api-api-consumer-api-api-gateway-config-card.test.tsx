import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-api-consumer-api-api-api-consumer-api-api-gateway-config-card";

describe("ConsumerApiGatewayConfigCard", () => {
  it("shows config", () => {
    const { container } = render(<Card consumerId="c1" timeoutMs={5000} maxRequestSize={1048576} compression={true} cors={true} logLevel="info" blockedPaths={["/admin"]} appName="App" />);
    expect(container.textContent).toContain("Gateway Config");
    expect(container.textContent).toContain("5000ms");
    expect(container.textContent).toContain("1.0 MB");
    expect(container.textContent).toContain("/admin");
  });
  it("shows defaults", () => {
    const { container } = render(<Card consumerId="c1" timeoutMs={30000} maxRequestSize={1024} compression={false} cors={false} logLevel="error" blockedPaths={[]} appName="App" />);
    expect(container.textContent).toContain("30000ms");
    expect(container.textContent).toContain("OFF");
  });
});
