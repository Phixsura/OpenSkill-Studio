import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DatabaseMigrationPanel } from "@/components/database-migration-panel";

describe("DatabaseMigrationPanel", () => {
  const migrations = [
    { migration_id: "001_init", name: "Init", status: "applied" },
    { migration_id: "002_users", name: "Add users", status: "pending" },
  ];
  it("renders", () => {
    const { container } = render(
      <DatabaseMigrationPanel migrations={migrations} currentVersion="001_init"
        upToDate={false} onApply={vi.fn()} onRollback={vi.fn()} />
    );
    expect(container.textContent).toContain("Migrations");
    expect(container.textContent).toContain("⏳ Pending");
    expect(container.textContent).toContain("Init");
    expect(container.textContent).toContain("applied");
    expect(container.textContent).toContain("pending");
  });
  it("apply", () => {
    const fn = vi.fn();
    const { container } = render(
      <DatabaseMigrationPanel migrations={migrations} currentVersion="001"
        upToDate={false} onApply={fn} onRollback={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Apply Pending")!);
    expect(fn).toHaveBeenCalled();
  });
});
