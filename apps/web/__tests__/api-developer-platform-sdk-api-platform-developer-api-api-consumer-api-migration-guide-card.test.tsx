import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-migration-guide-card";

describe("MigrationGuideCard", () => {
  it("shows guides", () => {
    const guides = [{ guide_id: "g1", from_version: "v1", to_version: "v2", steps: [{ step_id: "s1", title: "Update", breaking: true, difficulty: "medium" }], estimated_hours: 2.5, breaking_count: 1 }];
    const { container } = render(<Card guides={guides} appName="App" />);
    expect(container.textContent).toContain("Migration Guides");
    expect(container.textContent).toContain("v1 → v2");
    expect(container.textContent).toContain("~2.5h");
    expect(container.textContent).toContain("1 breaking");
  });
  it("shows empty", () => {
    const { container } = render(<Card guides={[]} appName="App" />);
    expect(container.textContent).toContain("No migration guides");
  });
});
