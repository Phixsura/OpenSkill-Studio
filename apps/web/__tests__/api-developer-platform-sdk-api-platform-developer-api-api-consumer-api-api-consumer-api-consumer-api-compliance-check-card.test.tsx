import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-compliance-check-card";

describe("ConsumerApiComplianceCheckCard", () => {
  it("shows compliance results", () => {
    const results = [{ ruleId: "r1", name: "HTTPS Only", passed: true, severity: "critical" }, { ruleId: "r2", name: "Logging", passed: false, severity: "warning" }];
    const { container } = render(<Card results={results} score={50} passed={1} failed={1} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Compliance");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("HTTPS Only");
    expect(container.textContent).toContain("✓");
    expect(container.textContent).toContain("✗");
  });
  it("shows perfect score", () => {
    const { container } = render(<Card results={[]} score={100} passed={5} failed={0} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("100%");
  });
});
