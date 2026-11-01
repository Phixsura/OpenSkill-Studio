import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import TagManagerCard from "../src/components/tag-manager-card";

const tags = [
  { tag: "env:prod", count: 5 },
  { tag: "env:staging", count: 3 },
  { tag: "team:backend", count: 4 },
  { tag: "important", count: 2 },
];

describe("TagManagerCard", () => {
  it("renders header and app name", () => {
    const { container } = render(
      <TagManagerCard tags={tags} appName="My App" totalResources={10} />,
    );
    expect(container.textContent).toContain("Tags");
    expect(container.textContent).toContain("My App");
  });

  it("shows tag and resource counts", () => {
    const { container } = render(<TagManagerCard tags={tags} appName="App" totalResources={10} />);
    expect(container.textContent).toContain("4 tags");
    expect(container.textContent).toContain("10 resources");
  });

  it("renders tag names", () => {
    const { container } = render(<TagManagerCard tags={tags} appName="App" totalResources={0} />);
    expect(container.textContent).toContain("env:prod");
    expect(container.textContent).toContain("team:backend");
    expect(container.textContent).toContain("important");
  });

  it("shows tag counts", () => {
    const { container } = render(<TagManagerCard tags={tags} appName="App" totalResources={0} />);
    expect(container.textContent).toContain("5");
    expect(container.textContent).toContain("3");
  });

  it("shows empty state", () => {
    const { container } = render(<TagManagerCard tags={[]} appName="App" totalResources={0} />);
    expect(container.textContent).toContain("No tags");
  });
});
