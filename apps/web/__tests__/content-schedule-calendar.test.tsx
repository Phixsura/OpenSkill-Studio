import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ContentScheduleCalendar } from "@/components/content-schedule-calendar";

describe("ContentScheduleCalendar", () => {
  const dates = {
    "2099-01-01": [
      { title: "Release Notes", content_type: "changelog", publish_at: "2099-01-01T09:00:00", status: "scheduled" },
    ],
  };
  it("renders", () => {
    const { container } = render(
      <ContentScheduleCalendar dates={dates} totalScheduled={1} onEdit={vi.fn()} />
    );
    expect(container.textContent).toContain("Content Schedule");
    expect(container.textContent).toContain("1 scheduled");
    expect(container.textContent).toContain("Release Notes");
    expect(container.textContent).toContain("📋");
    expect(container.textContent).toContain("09:00");
  });
});
