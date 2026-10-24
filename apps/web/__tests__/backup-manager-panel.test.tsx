import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { BackupManagerPanel } from "@/components/backup-manager-panel";

describe("BackupManagerPanel", () => {
  const backups = [
    { backup_id: "bak_1", type: "full", size_mb: 512, status: "completed", created_at: "2026-10-23T03:00:00" },
  ];
  it("renders", () => {
    const { container } = render(
      <BackupManagerPanel backups={backups} totalSizeMb={512} onCreateBackup={vi.fn()} onRestore={vi.fn()} onDelete={vi.fn()} />
    );
    expect(container.textContent).toContain("Backups");
    expect(container.textContent).toContain("bak_1");
    expect(container.textContent).toContain("512 MB");
    expect(container.textContent).toContain("full");
  });
  it("restore", () => {
    const fn = vi.fn();
    const { container } = render(
      <BackupManagerPanel backups={backups} totalSizeMb={512} onCreateBackup={vi.fn()} onRestore={fn} onDelete={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Restore")!);
    expect(fn).toHaveBeenCalledWith("bak_1");
  });
});
