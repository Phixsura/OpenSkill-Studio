import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-compliance-check-card";

describe("ComplianceCheckCard", () => {
  it("shows compliance", () => {
    const results = [{ consumer_id: "c1", compliant: 3, non_compliant: 1, total_rules: 4, overall: "non_compliant" }];
    const { container } = render(<Card results={results} nonCompliantCount={1} appName="App" />);
    expect(container.textContent).toContain("Compliance");
    expect(container.textContent).toContain("1 non-compliant");
    expect(container.textContent).toContain("3/4");
  });
  it("shows empty", () => {
    const { container } = render(<Card results={[]} nonCompliantCount={0} appName="App" />);
    expect(container.textContent).toContain("No compliance data");
  });
});
