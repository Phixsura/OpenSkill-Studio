import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-provider-integration-status-card";

describe("ProviderIntegrationStatusCard", () => {
  it("shows providers", () => {
    const providers = [{ id: "stripe", name: "Stripe", status: "operational", latencyMs: 50, error: "" }, { id: "twilio", name: "Twilio", status: "degraded", latencyMs: 500, error: "Slow" }];
    const { container } = render(<Card providers={providers} overall="degraded" operational={1} degraded={1} outage={0} appName="App" />);
    expect(container.textContent).toContain("Provider Status");
    expect(container.textContent).toContain("Stripe");
    expect(container.textContent).toContain("Twilio");
    expect(container.textContent).toContain("degraded");
  });
  it("shows empty", () => {
    const { container } = render(<Card providers={[]} overall="operational" operational={0} degraded={0} outage={0} appName="App" />);
    expect(container.textContent).toContain("No providers");
  });
});
