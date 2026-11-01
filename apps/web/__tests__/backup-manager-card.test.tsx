import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import BackupManagerCard from "../src/components/backup-manager-card";

const backups = [
  {
    backup_id: "b1",
    status: "completed" as const,
    size_mb: 150,
    label: "Daily backup",
    created_at: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    backup_id: "b2",
    status: "pending" as const,
    size_mb: 0,
    label: "",
    created_at: new Date(Date.now() - 60000).toISOString(),
  },
];

describe("BackupManagerCard", () => {
  it("renders header", () => {
    const { container } = render(
      <BackupManagerCard backups={backups} totalSizeMb={150} appName="My App" />,
    );
    expect(container.textContent).toContain("Backups");
  });

  it("shows backup count and size", () => {
    const { container } = render(
      <BackupManagerCard backups={backups} totalSizeMb={150} appName="App" />,
    );
    expect(container.textContent).toContain("2 backups");
    expect(container.textContent).toContain("150 MB");
  });

  it("renders labels and status", () => {
    const { container } = render(
      <BackupManagerCard backups={backups} totalSizeMb={0} appName="App" />,
    );
    expect(container.textContent).toContain("Daily backup");
    expect(container.textContent).toContain("✅");
    expect(container.textContent).toContain("⏳");
  });

  it("shows empty state", () => {
    const { container } = render(<BackupManagerCard backups={[]} totalSizeMb={0} appName="App" />);
    expect(container.textContent).toContain("No backups");
  });
});
