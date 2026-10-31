import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MaintWindowCalendar } from "@/components/maint-window-calendar";

describe("MaintWindowCalendar", () => {
  it("renders windows", () => {
    const { container } = render(
      <MaintWindowCalendar inMaintenance={true} activeCount={1} upcoming={1}
        windows={[
          { title: "DB Upgrade", durationMin: 30, affectedServices: ["database"], status: "active", startDisplay: "Now" },
          { title: "Cert Renewal", durationMin: 15, affectedServices: ["api"], status: "scheduled", startDisplay: "Tomorrow" },
        ]} />
    );
    expect(container.textContent).toContain("Maintenance Windows");
    expect(container.textContent).toContain("Active Now");
    expect(container.textContent).toContain("DB Upgrade");
    expect(container.textContent).toContain("30min");
    expect(container.textContent).toContain("database");
    expect(container.textContent).toContain("Cert Renewal");
  });
});
