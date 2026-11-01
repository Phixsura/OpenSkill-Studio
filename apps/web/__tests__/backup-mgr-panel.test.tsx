import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { BackupMgrPanel } from "@/components/backup-mgr-panel";

describe("BackupMgrPanel", () => {
  it("renders", () => {
    const { container } = render(
      <BackupMgrPanel totalSizeMb={562.5} retentionDays={30}
        backups={[
          { name: "db-2026-10-24", sizeMb: 512.5, type: "full", status: "completed" },
          { name: "db-inc", sizeMb: 50, type: "incremental", status: "completed" },
        ]} />
    );
    expect(container.textContent).toContain("Backups");
    expect(container.textContent).toContain("2 backups");
    expect(container.textContent).toContain("562.5MB");
    expect(container.textContent).toContain("30d retention");
    expect(container.textContent).toContain("db-2026-10-24");
    expect(container.textContent).toContain("full");
  });
});
