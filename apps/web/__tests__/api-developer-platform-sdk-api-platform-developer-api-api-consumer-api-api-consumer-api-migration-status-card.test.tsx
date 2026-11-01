import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-migration-status-card";

describe("ConsumerApiMigrationStatusCard", () => {
  it("shows migrations", () => {
    const migrations = [{ consumer_id: "c1", from_version: "v1", to_version: "v2", state: "in_progress", progress_pct: 65 }];
    const { container } = render(<Card migrations={migrations} inProgressCount={1} appName="App" />);
    expect(container.textContent).toContain("Migration Status");
    expect(container.textContent).toContain("v1 → v2");
    expect(container.textContent).toContain("1 migrating");
  });
  it("shows empty", () => {
    const { container } = render(<Card migrations={[]} inProgressCount={0} appName="App" />);
    expect(container.textContent).toContain("No migrations");
  });
});
