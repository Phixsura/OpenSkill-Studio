import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { BackupRestorePanel } from "@/components/backup-restore-panel";

describe("BackupRestorePanel", () => {
  it("renders backups", () => {
    const backups = [{ backup_id: "bak_1", created_at: "2026-01-01T00:00:00Z", size_bytes: 2048, webhooks_count: 1, secrets_count: 0 }];
    const { container } = render(<BackupRestorePanel backups={backups} onBackup={vi.fn()} onRestore={vi.fn()} />);
    expect(container.textContent).toContain("bak_1");
    expect(container.textContent).toContain("2KB");
  });
  it("empty state", () => {
    const { container } = render(<BackupRestorePanel backups={[]} onBackup={vi.fn()} onRestore={vi.fn()} />);
    expect(container.textContent).toContain("No backups");
  });
  it("calls onBackup", () => {
    const fn = vi.fn();
    const { container } = render(<BackupRestorePanel backups={[]} onBackup={fn} onRestore={vi.fn()} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
});
