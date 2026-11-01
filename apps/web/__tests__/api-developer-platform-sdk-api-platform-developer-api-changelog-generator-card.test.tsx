import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-changelog-generator-card";

describe("ChangelogGeneratorCard", () => {
  it("shows changelog", () => {
    const changes = [{ change_id: "c1", change_type: "added", description: "New endpoint", breaking: false }, { change_id: "c2", change_type: "removed", description: "Old auth", breaking: true }];
    const { container } = render(<Card version="v2.0" changes={changes} breakingCount={1} appName="App" />);
    expect(container.textContent).toContain("Changelog");
    expect(container.textContent).toContain("v2.0");
    expect(container.textContent).toContain("1 breaking");
    expect(container.textContent).toContain("New endpoint");
    expect(container.textContent).toContain("BREAKING");
  });
  it("shows empty", () => {
    const { container } = render(<Card version="v1.0" changes={[]} breakingCount={0} appName="App" />);
    expect(container.textContent).toContain("No changes");
  });
});
