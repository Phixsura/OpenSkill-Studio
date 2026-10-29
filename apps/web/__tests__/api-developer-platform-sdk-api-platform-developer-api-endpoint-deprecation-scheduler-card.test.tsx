import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-endpoint-deprecation-scheduler-card";

describe("DeprecationSchedulerCard", () => {
  it("shows schedules", () => {
    const schedules = [{ endpoint: "/api/v1/old", method: "GET", phase: "warning", replacement: "/v2", active_consumers: 12, days_until_sunset: 30 }];
    const { container } = render(<Card schedules={schedules} overdueCount={0} appName="App" />);
    expect(container.textContent).toContain("Deprecation Schedule");
    expect(container.textContent).toContain("/api/v1/old");
    expect(container.textContent).toContain("warning");
    expect(container.textContent).toContain("12 consumers");
    expect(container.textContent).toContain("30d left");
  });
  it("shows overdue", () => {
    const schedules = [{ endpoint: "/old", method: "DELETE", phase: "sunset", replacement: "", active_consumers: 0, days_until_sunset: -5 }];
    const { container } = render(<Card schedules={schedules} overdueCount={1} appName="App" />);
    expect(container.textContent).toContain("1 overdue");
    expect(container.textContent).toContain("overdue");
  });
});
