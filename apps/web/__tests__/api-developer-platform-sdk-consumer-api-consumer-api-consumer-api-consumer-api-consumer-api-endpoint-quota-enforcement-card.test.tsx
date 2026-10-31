import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-consumer-api-consumer-api-consumer-api-consumer-api-endpoint-quota-enforcement-card";

describe("EndpointQuotaEnforcementCard", () => {
  it("shows quotas", () => {
    const quotas = [{ endpoint: "/api/users", current: 85, limit: 100, remaining: 15, windowSec: 3600 }];
    const { container } = render(<Card quotas={quotas} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Quota Enforcement");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("85/100");
  });
  it("shows empty", () => {
    const { container } = render(<Card quotas={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No endpoint quotas");
  });
});
