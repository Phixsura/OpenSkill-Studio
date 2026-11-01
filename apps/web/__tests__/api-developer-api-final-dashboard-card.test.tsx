import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIFinalDashboardCard from "../src/components/api-developer-api-final-dashboard-card";

const dash = {
  platform_health_grade: "A", api_performance_grade: "A", webhook_delivery_grade: "A",
  developer_experience_grade: "B", documentation_grade: "A", security_grade: "A",
  overall_grade: "A", total_developers: 500, total_api_calls: 10000000, overall_uptime: 99.99, nps_score: 70,
};

describe("APIDeveloperAPIFinalDashboardCard", () => {
  it("shows the complete dashboard", () => {
    const { container } = render(<APIDeveloperAPIFinalDashboardCard dashboard={dash} appName="OpenSkill Studio" />);
    expect(container.textContent).toContain("Developer Platform Dashboard");
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("10,000,000");
    expect(container.textContent).toContain("99.99%");
    expect(container.textContent).toContain("70");
  });
});
