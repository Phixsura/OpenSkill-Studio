import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ComplianceReportCard from "../src/components/compliance-report-card";

const errorViolation = {
  rule_id: "r1",
  rule_name: "Privacy Policy Required",
  message: "Required field 'privacy_url' is missing",
  severity: "error" as const,
  field: "privacy_url",
};
const warningViolation = {
  rule_id: "r2",
  rule_name: "Description Length",
  message: "Field 'description' exceeds max size 500",
  severity: "warning" as const,
  field: "description",
};

describe("ComplianceReportCard", () => {
  it("renders header and app name", () => {
    const { container } = render(
      <ComplianceReportCard compliant violations={[]} rulesChecked={5} appName="My App" />,
    );
    expect(container.textContent).toContain("Compliance");
    expect(container.textContent).toContain("My App");
  });

  it("shows compliant badge", () => {
    const { container } = render(
      <ComplianceReportCard compliant violations={[]} rulesChecked={3} appName="App" />,
    );
    expect(container.textContent).toContain("Compliant");
  });

  it("shows non-compliant badge", () => {
    const { container } = render(
      <ComplianceReportCard
        compliant={false}
        violations={[errorViolation]}
        rulesChecked={3}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("Non-compliant");
  });

  it("shows rules checked count", () => {
    const { container } = render(
      <ComplianceReportCard compliant violations={[]} rulesChecked={5} appName="App" />,
    );
    expect(container.textContent).toContain("5 rules checked");
  });

  it("shows all-passed message", () => {
    const { container } = render(
      <ComplianceReportCard compliant violations={[]} rulesChecked={3} appName="App" />,
    );
    expect(container.textContent).toContain("All compliance checks passed");
  });

  it("renders error violations", () => {
    const { container } = render(
      <ComplianceReportCard
        compliant={false}
        violations={[errorViolation]}
        rulesChecked={3}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("Privacy Policy Required");
    expect(container.textContent).toContain("privacy_url");
  });

  it("renders warning violations", () => {
    const { container } = render(
      <ComplianceReportCard
        compliant
        violations={[warningViolation]}
        rulesChecked={3}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("Description Length");
  });

  it("renders mixed violations", () => {
    const { container } = render(
      <ComplianceReportCard
        compliant={false}
        violations={[errorViolation, warningViolation]}
        rulesChecked={3}
        appName="App"
      />,
    );
    expect(container.textContent).toContain("✕");
    expect(container.textContent).toContain("⚠");
  });
});
