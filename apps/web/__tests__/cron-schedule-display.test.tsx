import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CronScheduleDisplay } from "@/components/cron-schedule-display";

describe("CronScheduleDisplay", () => {
  const fields = { minute: "30", hour: "9", day_of_month: "*", month: "*", day_of_week: "*" };
  it("renders", () => {
    const { container } = render(
      <CronScheduleDisplay expression="30 9 * * *" description="At 09:30" fields={fields} />
    );
    expect(container.textContent).toContain("At 09:30");
    expect(container.textContent).toContain("30 9 * * *");
    expect(container.textContent).toContain("Minute");
    expect(container.textContent).toContain("Hour");
    expect(container.textContent).toContain("30");
    expect(container.textContent).toContain("9");
  });
});
