import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import HealthReportCard from "../src/components/api-developer-platform-sdk-consumer-api-health-report-card";

describe("HealthReportCard", () => {
  it("renders title and reports", () => {
    const { container } = render(<HealthReportCard />);
    expect(container.textContent).toContain("Health Reports");
    expect(container.textContent).toContain("Oct 2024");
    expect(container.textContent).toContain("Aug 2024");
  });

  it("shows grades and count", () => {
    const { container } = render(<HealthReportCard />);
    expect(container.textContent).toContain("95%");
    expect(container.textContent).toContain("3 reports generated");
  });
});
