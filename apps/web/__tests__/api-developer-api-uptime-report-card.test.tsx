import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIUptimeReportCard from "../src/components/api-developer-api-uptime-report-card";

const reports = [{ report_id: "r1", period: "2024-01", uptime_pct: 99.95, downtime_minutes: 21.6, incidents: 1 }];

describe("APIDeveloperAPIUptimeReportCard", () => {
  it("shows reports", () => {
    const { container } = render(<APIDeveloperAPIUptimeReportCard reports={reports} appName="App" />);
    expect(container.textContent).toContain("Uptime Reports");
    expect(container.textContent).toContain("2024-01");
    expect(container.textContent).toContain("99.95%");
    expect(container.textContent).toContain("21.6min down");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIUptimeReportCard reports={[]} appName="App" />);
    expect(container.textContent).toContain("No uptime reports");
  });
});
