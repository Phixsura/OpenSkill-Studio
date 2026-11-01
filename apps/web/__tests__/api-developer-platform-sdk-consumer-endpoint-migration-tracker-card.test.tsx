import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-endpoint-migration-tracker-card";

describe("EndpointMigrationTrackerCard", () => {
  it("shows migrations", () => {
    const migrations = [{ oldEndpoint: "/v1/users", newEndpoint: "/v2/users", deadline: "2026-07-01", status: "pending" }];
    const { container } = render(<Card migrations={migrations} completedCount={0} totalCount={1} progressPct={0} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Migration Tracker");
    expect(container.textContent).toContain("/v1/users");
    expect(container.textContent).toContain("/v2/users");
    expect(container.textContent).toContain("pending");
    expect(container.textContent).toContain("0/1");
  });
  it("shows empty", () => {
    const { container } = render(<Card migrations={[]} completedCount={0} totalCount={0} progressPct={0} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No migrations");
  });
});
