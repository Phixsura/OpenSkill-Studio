import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ImpactReportPanel } from "@/components/impact-report-panel";

const report = {
  hoursSaved: 40, errorsPrevented: 150, tasksAutomated: 500, usersImpacted: 200,
  costSavings: 200000, productivityGain: 35, annualHoursSaved: 480, annualSavings: 2400000,
};

describe("ImpactReportPanel", () => {
  it("renders impact metrics", () => {
    const { container } = render(<ImpactReportPanel report={report} extensionName="Slack Bot" />);
    expect(container.textContent).toContain("40");
    expect(container.textContent).toContain("150");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("480h");
    expect(container.textContent).toContain("+35%");
  });
});
