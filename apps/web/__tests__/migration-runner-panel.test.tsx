import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MigrationRunnerPanel } from "@/components/migration-runner-panel";

const mockMigrations = [
  { migrationId: "m1", version: "001", name: "create_users", state: "applied" as const },
  { migrationId: "m2", version: "002", name: "add_email", state: "applied" as const },
  { migrationId: "m3", version: "003", name: "add_roles", state: "pending" as const },
];
const mockStatus = { total: 3, applied: 2, pending: 1, failed: 0, currentVersion: "002" };

describe("MigrationRunnerPanel", () => {
  it("renders migrations and status", () => {
    const { container } = render(
      <MigrationRunnerPanel migrations={mockMigrations} status={mockStatus} />
    );
    expect(container.textContent).toContain("create_users");
    expect(container.textContent).toContain("v002");
    expect(container.textContent).toContain("add_roles");
  });

  it("shows stats grid", () => {
    const { container } = render(
      <MigrationRunnerPanel migrations={mockMigrations} status={mockStatus} />
    );
    expect(container.textContent).toContain("2"); // applied
    expect(container.textContent).toContain("1"); // pending
  });

  it("calls onMigrateUp", () => {
    const onUp = vi.fn();
    const { getByText } = render(
      <MigrationRunnerPanel migrations={mockMigrations} status={mockStatus} onMigrateUp={onUp} />
    );
    fireEvent.click(getByText("Migrate Up"));
    expect(onUp).toHaveBeenCalled();
  });

  it("calls onRollbackLast", () => {
    const onRollback = vi.fn();
    const { getByText } = render(
      <MigrationRunnerPanel migrations={mockMigrations} status={mockStatus} onRollbackLast={onRollback} />
    );
    fireEvent.click(getByText("Rollback"));
    expect(onRollback).toHaveBeenCalled();
  });
});
