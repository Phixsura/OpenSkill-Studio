import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ConformanceReportCard } from "@/components/conformance-report-card";

const CHECKS = [
  { name: "manifest", status: "pass", message: "Valid" },
  { name: "security", status: "pass", message: "No issues" },
  { name: "health", status: "fail", message: "Score too low" },
];

describe("ConformanceReportCard", () => {
  it("shows app name and version", () => {
    const { container } = render(<ConformanceReportCard appName="Test" version="1.0.0" passed={false} checks={CHECKS} checkedAt="now" />);
    expect(container.textContent).toContain("Test v1.0.0");
  });

  it("shows pass count", () => {
    const { container } = render(<ConformanceReportCard appName="X" version="1.0" passed={false} checks={CHECKS} checkedAt="now" />);
    expect(container.textContent).toContain("2/3");
  });

  it("shows passed badge", () => {
    const { container } = render(<ConformanceReportCard appName="X" version="1.0" passed={true} checks={[CHECKS[0]]} checkedAt="now" />);
    expect(container.textContent).toContain("Passed");
  });

  it("shows failed badge", () => {
    const { container } = render(<ConformanceReportCard appName="X" version="1.0" passed={false} checks={CHECKS} checkedAt="now" />);
    expect(container.textContent).toContain("Failed");
  });

  it("lists check messages", () => {
    const { container } = render(<ConformanceReportCard appName="X" version="1.0" passed={false} checks={CHECKS} checkedAt="now" />);
    expect(container.textContent).toContain("Score too low");
  });
});
