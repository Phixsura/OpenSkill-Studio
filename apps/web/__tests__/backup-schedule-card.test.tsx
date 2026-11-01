import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { BackupScheduleCard } from "@/components/backup-schedule-card";

describe("BackupScheduleCard", () => {
  it("renders schedule", () => {
    const { container } = render(
      <BackupScheduleCard name="Nightly" frequency="daily" retentionDays={7}
        targets={["database", "files"]} totalBackups={30} totalSizeMb={4500} onRunNow={vi.fn()} />
    );
    expect(container.textContent).toContain("Nightly");
    expect(container.textContent).toContain("daily");
    expect(container.textContent).toContain("7d retention");
    expect(container.textContent).toContain("30");
    expect(container.textContent).toContain("4500");
    expect(container.textContent).toContain("database");
    expect(container.textContent).toContain("Run Now");
  });
});
