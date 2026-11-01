import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MaintenanceBanner } from "@/components/maintenance-banner";

describe("MaintenanceBanner", () => {
  it("renders active and upcoming", () => {
    const { container } = render(
      <MaintenanceBanner windows={[
        { id: "mw-1", title: "DB Upgrade", start: "02:00", end: "04:00",
          affected: ["database", "api"], severity: "full", status: "in_progress" },
        { id: "mw-2", title: "Network Patch", start: "06:00", end: "07:00",
          affected: ["network"], severity: "partial", status: "scheduled" },
      ]} />
    );
    expect(container.textContent).toContain("Maintenance in Progress");
    expect(container.textContent).toContain("DB Upgrade");
    expect(container.textContent).toContain("database, api");
    expect(container.textContent).toContain("Scheduled Maintenance");
    expect(container.textContent).toContain("Network Patch");
  });
});
