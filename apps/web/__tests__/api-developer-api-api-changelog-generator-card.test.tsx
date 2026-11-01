import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiChangelogGeneratorCard from "../src/components/api-developer-api-api-changelog-generator-card";

const changelogs = [
  { version: "v2.0", entries: [{ entry_id: "e1", category: "added", description: "New endpoint", breaking: true }], published: true, breaking_count: 1 },
];

describe("APIDeveloperAPIApiChangelogGeneratorCard", () => {
  it("shows changelogs", () => {
    const { container } = render(<APIDeveloperAPIApiChangelogGeneratorCard changelogs={changelogs} appName="App" />);
    expect(container.textContent).toContain("Changelog Generator");
    expect(container.textContent).toContain("v2.0");
    expect(container.textContent).toContain("published");
    expect(container.textContent).toContain("1 breaking");
    expect(container.textContent).toContain("New endpoint");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiChangelogGeneratorCard changelogs={[]} appName="App" />);
    expect(container.textContent).toContain("No changelogs");
  });
});
