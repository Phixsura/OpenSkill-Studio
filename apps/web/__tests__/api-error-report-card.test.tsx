import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIErrorReportCard from "../src/components/api-error-report-card";

const reports = [{ report_id: "r1", period: "2024-01", errors: [{ error_code: "AUTH", count: 50 }], total_errors: 80, error_rate: 0.8 }];

describe("APIErrorReportCard", () => {
  it("shows report", () => {
    const { container } = render(<APIErrorReportCard reports={reports} appName="App" />);
    expect(container.textContent).toContain("2024-01");
    expect(container.textContent).toContain("0.8% error rate");
    expect(container.textContent).toContain("80 errors");
  });
  it("shows empty", () => {
    const { container } = render(<APIErrorReportCard reports={[]} appName="App" />);
    expect(container.textContent).toContain("No error reports");
  });
});
