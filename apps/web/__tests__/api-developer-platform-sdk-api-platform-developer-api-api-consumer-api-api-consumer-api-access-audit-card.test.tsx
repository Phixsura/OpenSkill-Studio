import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-access-audit-card";

describe("ConsumerApiAccessAuditCard", () => {
  it("shows audit stats", () => {
    const reasons = [{ reason: "rate_limited", count: 50 }, { reason: "scope_denied", count: 10 }];
    const { container } = render(<Card totalEntries={10000} denialRate={3.5} reasons={reasons} appName="App" />);
    expect(container.textContent).toContain("Access Audit");
    expect(container.textContent).toContain("10,000 entries");
    expect(container.textContent).toContain("3.5% denied");
    expect(container.textContent).toContain("rate_limited");
  });
  it("shows zero denial", () => {
    const { container } = render(<Card totalEntries={0} denialRate={0} reasons={[]} appName="App" />);
    expect(container.textContent).toContain("0% denied");
  });
});
