import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import MigrationTrackerCard from "../src/components/migration-tracker-card";

const migrations = [
  {
    migration_id: "m1",
    version: "001",
    description: "Create users",
    status: "completed" as const,
    duration_ms: 120.5,
    error: "",
  },
  {
    migration_id: "m2",
    version: "002",
    description: "Add index",
    status: "failed" as const,
    duration_ms: 5000,
    error: "timeout",
  },
  {
    migration_id: "m3",
    version: "003",
    description: "Add column",
    status: "pending" as const,
    duration_ms: null,
    error: "",
  },
];

describe("MigrationTrackerCard", () => {
  it("renders header and counts", () => {
    const { container } = render(<MigrationTrackerCard migrations={migrations} appName="App" />);
    expect(container.textContent).toContain("Migration Tracker");
    expect(container.textContent).toContain("1 done");
    expect(container.textContent).toContain("1 failed");
  });

  it("shows versions and descriptions", () => {
    const { container } = render(<MigrationTrackerCard migrations={migrations} appName="App" />);
    expect(container.textContent).toContain("001");
    expect(container.textContent).toContain("Create users");
    expect(container.textContent).toContain("Add index");
  });

  it("shows status badges", () => {
    const { container } = render(<MigrationTrackerCard migrations={migrations} appName="App" />);
    expect(container.textContent).toContain("completed");
    expect(container.textContent).toContain("failed");
    expect(container.textContent).toContain("pending");
  });

  it("shows duration and errors", () => {
    const { container } = render(<MigrationTrackerCard migrations={migrations} appName="App" />);
    expect(container.textContent).toContain("120.5ms");
    expect(container.textContent).toContain("timeout");
  });

  it("shows empty state", () => {
    const { container } = render(<MigrationTrackerCard migrations={[]} appName="App" />);
    expect(container.textContent).toContain("No migrations");
  });
});
