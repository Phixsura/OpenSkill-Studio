import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import MigrationRunnerCard from "../src/components/migration-runner-card";

const appliedMigration = {
  migration_id: "m1",
  version: 1,
  description: "Create users table",
  status: "applied" as const,
  applied_at: new Date().toISOString(),
  duration_ms: 150,
  error: null,
};

const pendingMigration = {
  migration_id: "m2",
  version: 2,
  description: "Add email index",
  status: "pending" as const,
  applied_at: null,
  duration_ms: null,
  error: null,
};

const failedMigration = {
  migration_id: "m3",
  version: 3,
  description: "Migrate legacy data",
  status: "failed" as const,
  applied_at: null,
  duration_ms: null,
  error: "connection timeout",
};

describe("MigrationRunnerCard", () => {
  it("renders header and app name", () => {
    const { container } = render(
      <MigrationRunnerCard migrations={[appliedMigration]} appName="My App" currentVersion={1} />,
    );
    expect(container.textContent).toContain("Migrations");
    expect(container.textContent).toContain("My App");
  });

  it("shows current version", () => {
    const { container } = render(
      <MigrationRunnerCard migrations={[appliedMigration]} appName="App" currentVersion={3} />,
    );
    expect(container.textContent).toContain("v3");
  });

  it("shows pending count", () => {
    const { container } = render(
      <MigrationRunnerCard
        migrations={[appliedMigration, pendingMigration, failedMigration]}
        appName="App"
        currentVersion={1}
      />,
    );
    expect(container.textContent).toContain("2 pending");
  });

  it("renders migration description and version", () => {
    const { container } = render(
      <MigrationRunnerCard migrations={[appliedMigration]} appName="App" currentVersion={1} />,
    );
    expect(container.textContent).toContain("Create users table");
    expect(container.textContent).toContain("v1");
  });

  it("shows duration for applied", () => {
    const { container } = render(
      <MigrationRunnerCard migrations={[appliedMigration]} appName="App" currentVersion={1} />,
    );
    expect(container.textContent).toContain("150ms");
  });

  it("shows error for failed", () => {
    const { container } = render(
      <MigrationRunnerCard migrations={[failedMigration]} appName="App" currentVersion={0} />,
    );
    expect(container.textContent).toContain("connection timeout");
  });

  it("shows status labels", () => {
    const { container } = render(
      <MigrationRunnerCard
        migrations={[appliedMigration, pendingMigration]}
        appName="App"
        currentVersion={1}
      />,
    );
    expect(container.textContent).toContain("applied");
    expect(container.textContent).toContain("pending");
  });

  it("shows empty state", () => {
    const { container } = render(
      <MigrationRunnerCard migrations={[]} appName="App" currentVersion={0} />,
    );
    expect(container.textContent).toContain("No migrations");
  });
});
