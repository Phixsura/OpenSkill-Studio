import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { BackupStatusPanel } from "@/components/backup-status-panel";

describe("BackupStatusPanel", () => {
  it("renders backups", () => {
    const onBackup = vi.fn();
    const { container, getByText } = render(
      <BackupStatusPanel onBackupNow={onBackup} summary={{
        totalBackups: 3, byDatabase: { primary: 2, analytics: 1 },
        totalSizeMb: 4700, verifiedCount: 1, unverifiedCount: 2,
      }} />
    );
    expect(container.textContent).toContain("Database Backups");
    expect(container.textContent).toContain("3");
    expect(container.textContent).toContain("4.6 GB");
    expect(container.textContent).toContain("primary");
    expect(container.textContent).toContain("2 backups");
    fireEvent.click(getByText("Backup Now"));
    expect(onBackup).toHaveBeenCalled();
  });
});
