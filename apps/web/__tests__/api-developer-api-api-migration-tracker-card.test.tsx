import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiMigrationTrackerCard from "../src/components/api-developer-api-api-migration-tracker-card";

const tasks = [
  { task_id: "t1", consumer_id: "acme", from_version: "v1", to_version: "v2", status: "completed" },
  { task_id: "t2", consumer_id: "beta", from_version: "v1", to_version: "v2", status: "pending" },
];

describe("APIDeveloperAPIApiMigrationTrackerCard", () => {
  it("shows migrations", () => {
    const { container } = render(<APIDeveloperAPIApiMigrationTrackerCard tasks={tasks} progress={{ pending: 1, in_progress: 0, completed: 1, failed: 0 }} appName="App" />);
    expect(container.textContent).toContain("Migration Tracker");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("acme");
    expect(container.textContent).toContain("v1 → v2");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiMigrationTrackerCard tasks={[]} progress={{}} appName="App" />);
    expect(container.textContent).toContain("No migrations");
  });
});
