import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { BackupStatusPanel } from "@/components/backup-status-panel";

describe("BackupStatusPanel", () => {
  const backups = [
    { id: "bak_1", status: "completed", sizeMb: 150, createdAt: "2026-01-03" },
    { id: "bak_2", status: "failed", sizeMb: 0, createdAt: "2026-01-02" },
  ];
  it("renders backups", () => {
    const { container } = render(
      <BackupStatusPanel backups={backups} totalSizeMb={150} successCount={1} total={2} />
    );
    expect(container.textContent).toContain("bak_1");
    expect(container.textContent).toContain("150MB");
    expect(container.textContent).toContain("1/2");
  });
});
