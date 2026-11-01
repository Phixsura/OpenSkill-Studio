import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIMigrationStatusCard from "../src/components/api-developer-api-migration-status-card";

const migrations = [
  { consumer_id: "app-1", from_version: "v1", to_version: "v2", migrated: true },
  { consumer_id: "app-2", from_version: "v1", to_version: "v2", migrated: false },
];
const progress = { total: 2, migrated: 1, pct: 50 };

describe("APIDeveloperAPIMigrationStatusCard", () => {
  it("shows progress", () => {
    const { container } = render(<APIDeveloperAPIMigrationStatusCard migrations={migrations} progress={progress} appName="App" />);
    expect(container.textContent).toContain("Migration Status");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("1/2 migrated");
    expect(container.textContent).toContain("app-2");
    expect(container.textContent).toContain("v1 → v2");
  });
});
