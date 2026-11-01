import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIRequestValidationReportCard from "../src/components/api-developer-api-request-validation-report-card";

const failures = [
  { endpoint: "/api/users", field: "email", rule: "format", count: 42 },
  { endpoint: "/api/users", field: "name", rule: "required", count: 15 },
];

describe("APIDeveloperAPIRequestValidationReportCard", () => {
  it("shows validation failures", () => {
    const { container } = render(<APIDeveloperAPIRequestValidationReportCard failures={failures} totalFailures={57} ruleBreakdown={{ format: 42, required: 15 }} appName="App" />);
    expect(container.textContent).toContain("Validation Report");
    expect(container.textContent).toContain("57");
    expect(container.textContent).toContain("format: 42");
    expect(container.textContent).toContain("email");
    expect(container.textContent).toContain("×42");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIRequestValidationReportCard failures={[]} totalFailures={0} ruleBreakdown={{}} appName="App" />);
    expect(container.textContent).toContain("No validation failures");
  });
});
