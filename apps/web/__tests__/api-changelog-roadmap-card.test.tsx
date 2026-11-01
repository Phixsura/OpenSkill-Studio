import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIChangelogRoadmapCard from "../src/components/api-changelog-roadmap-card";

const items = [
  { item_id: "i1", title: "Dark Mode", target_version: "v3.0", status: "planned", vote_count: 25 },
  { item_id: "i2", title: "GraphQL", target_version: "v3.0", status: "in_progress", vote_count: 15 },
];

describe("APIChangelogRoadmapCard", () => {
  it("shows roadmap items", () => {
    const { container } = render(<APIChangelogRoadmapCard items={items} appName="App" />);
    expect(container.textContent).toContain("Roadmap");
    expect(container.textContent).toContain("Dark Mode");
    expect(container.textContent).toContain("planned");
    expect(container.textContent).toContain("in progress");
    expect(container.textContent).toContain("👍 25");
  });
  it("shows empty", () => {
    const { container } = render(<APIChangelogRoadmapCard items={[]} appName="App" />);
    expect(container.textContent).toContain("No roadmap items");
  });
});
