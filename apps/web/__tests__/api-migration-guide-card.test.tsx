import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIMigrationGuideCard from "../src/components/api-migration-guide-card";

const guides = [
  { guide_id: "g1", from_version: "v1", to_version: "v2", step_count: 5, breaking_count: 2, completed_count: 10 },
  { guide_id: "g2", from_version: "v2", to_version: "v3", step_count: 3, breaking_count: 0, completed_count: 0 },
];

describe("APIMigrationGuideCard", () => {
  it("renders header and guide count", () => {
    const { container } = render(<APIMigrationGuideCard guides={guides} appName="App" />);
    expect(container.textContent).toContain("Migration Guides");
    expect(container.textContent).toContain("2 guides");
  });

  it("shows version transitions", () => {
    const { container } = render(<APIMigrationGuideCard guides={guides} appName="App" />);
    expect(container.textContent).toContain("v1 → v2");
    expect(container.textContent).toContain("v2 → v3");
  });

  it("shows breaking count and migrated", () => {
    const { container } = render(<APIMigrationGuideCard guides={guides} appName="App" />);
    expect(container.textContent).toContain("2 breaking");
    expect(container.textContent).toContain("10 migrated");
  });

  it("shows empty state", () => {
    const { container } = render(<APIMigrationGuideCard guides={[]} appName="App" />);
    expect(container.textContent).toContain("No migration guides");
  });
});
