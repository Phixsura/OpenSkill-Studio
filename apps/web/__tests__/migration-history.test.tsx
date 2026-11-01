import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MigrationHistory } from "@/components/migration-history";

describe("MigrationHistory", () => {
  const migrations = [
    { id: "001_init", name: "Init", status: "applied", createdAt: "2026-01-01" },
    { id: "002_users", name: "Add users", status: "pending", createdAt: "2026-01-02" },
  ];
  it("renders migrations", () => {
    const { container } = render(
      <MigrationHistory migrations={migrations} applied={1} pending={1} failed={0} needsMigration={true} />
    );
    expect(container.textContent).toContain("001_init");
    expect(container.textContent).toContain("1 applied");
    expect(container.textContent).toContain("1 pending");
    expect(container.textContent).toContain("pending migration");
  });
});
