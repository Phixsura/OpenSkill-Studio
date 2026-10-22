import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiChangelogView } from "@/components/api-changelog-view";

const VERSIONS = [{ version: "2024-01-01", date: "2024-01-01", changes: [{ type: "added", description: "New API" }] }];

describe("ApiChangelogView", () => {
  it("shows version", () => {
    const { container } = render(<ApiChangelogView versions={VERSIONS} />);
    expect(container.textContent).toContain("2024-01-01");
  });
  it("shows changes", () => {
    const { container } = render(<ApiChangelogView versions={VERSIONS} />);
    expect(container.textContent).toContain("New API");
    expect(container.textContent).toContain("✨");
  });
});
