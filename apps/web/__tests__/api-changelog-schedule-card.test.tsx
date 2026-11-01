import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIChangelogScheduleCard from "../src/components/api-changelog-schedule-card";

const schedules = [
  { schedule_id: "s1", version: "v3.0", title: "Major Release", publish_date: "2025-02-01", status: "scheduled" },
  { schedule_id: "s2", version: "v2.5", title: "Patch", publish_date: "2025-01-15", status: "published" },
];

describe("APIChangelogScheduleCard", () => {
  it("shows schedules", () => {
    const { container } = render(<APIChangelogScheduleCard schedules={schedules} appName="App" />);
    expect(container.textContent).toContain("Changelog Schedule");
    expect(container.textContent).toContain("1 upcoming");
    expect(container.textContent).toContain("Major Release");
    expect(container.textContent).toContain("2025-02-01");
  });
  it("shows empty", () => {
    const { container } = render(<APIChangelogScheduleCard schedules={[]} appName="App" />);
    expect(container.textContent).toContain("No scheduled releases");
  });
});
