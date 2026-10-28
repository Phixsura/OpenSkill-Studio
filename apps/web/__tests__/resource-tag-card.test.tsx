import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ResourceTagCard from "../src/components/resource-tag-card";

const tags = [
  { tag: "production", count: 5 },
  { tag: "critical", count: 3 },
  { tag: "staging", count: 2 },
];

describe("ResourceTagCard", () => {
  it("renders header and counts", () => {
    const { container } = render(<ResourceTagCard tags={tags} totalResources={10} appName="App" />);
    expect(container.textContent).toContain("Resource Tags");
    expect(container.textContent).toContain("3 tags");
    expect(container.textContent).toContain("10 resources");
  });

  it("shows tag names with counts", () => {
    const { container } = render(<ResourceTagCard tags={tags} totalResources={10} appName="App" />);
    expect(container.textContent).toContain("production");
    expect(container.textContent).toContain("5");
    expect(container.textContent).toContain("critical");
  });

  it("shows empty state", () => {
    const { container } = render(<ResourceTagCard tags={[]} totalResources={0} appName="App" />);
    expect(container.textContent).toContain("No tags");
  });
});
