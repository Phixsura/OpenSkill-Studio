import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MaintenanceBanner } from "@/components/maintenance-banner";

describe("MaintenanceBanner", () => {
  it("shows active maintenance", () => {
    const windows = [{ title: "DB Migration", start: "2026-01-01T02:00:00Z",
      end: "2026-01-01T04:00:00Z", status: "in_progress", services: ["database"] }];
    const { container } = render(<MaintenanceBanner windows={windows} hasActive={true} />);
    expect(container.textContent).toContain("Maintenance in progress");
    expect(container.textContent).toContain("DB Migration");
    expect(container.textContent).toContain("database");
  });
  it("shows upcoming", () => {
    const windows = [{ title: "Update", start: "2099-06-01T00:00:00Z",
      end: "2099-06-01T01:00:00Z", status: "scheduled", services: ["all"] }];
    const { container } = render(<MaintenanceBanner windows={windows} hasActive={false} />);
    expect(container.textContent).toContain("Upcoming");
    expect(container.textContent).toContain("Update");
  });
  it("hides when nothing", () => {
    const { container } = render(<MaintenanceBanner windows={[]} hasActive={false} />);
    expect(container.innerHTML).toBe("");
  });
});
