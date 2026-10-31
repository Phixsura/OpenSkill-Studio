import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CronScheduleEditor } from "@/components/cron-schedule-editor";

describe("CronScheduleEditor", () => {
  it("renders editor", () => {
    const { container } = render(
      <CronScheduleEditor expression="0 9 * * 1-5" description="At 9:00 on weekday 1-5"
        fields={{ minute: "0", hour: "9", day_of_month: "*", month: "*", day_of_week: "1-5" }}
        valid={true} onChange={vi.fn()} />
    );
    expect(container.textContent).toContain("Cron Schedule");
    expect(container.textContent).toContain("At 9:00");
    expect(container.textContent).toContain("minute: 0");
    expect(container.textContent).toContain("hour: 9");
    expect(container.textContent).toContain("Hourly");
  });
});
