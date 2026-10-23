import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MaintenanceWindowBanner } from "@/components/maintenance-window-banner";

describe("MaintenanceWindowBanner", () => {
  it("active maintenance", () => {
    const active = [{ window_id: "mw1", title: "DB Migration", start_time: "2026-10-23T03:00:00",
      end_time: "2026-10-23T04:00:00", duration_min: 60, affected_components: ["database"], status: "active" }];
    const { container } = render(<MaintenanceWindowBanner active={active} upcoming={[]} />);
    expect(container.textContent).toContain("Maintenance in Progress");
    expect(container.textContent).toContain("DB Migration");
    expect(container.textContent).toContain("database");
  });
  it("upcoming", () => {
    const upcoming = [{ window_id: "mw2", title: "API Update", start_time: "2026-11-01T03:00:00",
      end_time: "2026-11-01T04:00:00", duration_min: 60, affected_components: ["api"], status: "scheduled" }];
    const { container } = render(<MaintenanceWindowBanner active={[]} upcoming={upcoming} />);
    expect(container.textContent).toContain("Upcoming: API Update");
    expect(container.textContent).toContain("60min");
  });
  it("hidden when none", () => {
    const { container } = render(<MaintenanceWindowBanner active={[]} upcoming={[]} />);
    expect(container.innerHTML).toBe("");
  });
});
