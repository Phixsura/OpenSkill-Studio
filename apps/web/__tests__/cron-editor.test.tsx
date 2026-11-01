import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CronEditor } from "@/components/cron-editor";

describe("CronEditor", () => {
  const fields = [
    { field: "minute", value: "0", range: "0-59" },
    { field: "hour", value: "9", range: "0-23" },
    { field: "day_of_month", value: "*", range: "1-31" },
    { field: "month", value: "*", range: "1-12" },
    { field: "day_of_week", value: "1-5", range: "0-6" },
  ];
  it("renders fields", () => {
    const { container } = render(
      <CronEditor fields={fields} expression="0 9 * * 1-5" description="At 09:00 on Mon-Fri" onChange={vi.fn()} />
    );
    expect(container.textContent).toContain("minute");
    expect(container.textContent).toContain("0 9 * * 1-5");
    expect(container.textContent).toContain("At 09:00 on Mon-Fri");
    expect(container.querySelectorAll("input").length).toBe(5);
  });
});
