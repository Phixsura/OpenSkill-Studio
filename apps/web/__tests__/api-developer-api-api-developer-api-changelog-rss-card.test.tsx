import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiChangelogRssCard from "../src/components/api-developer-api-api-developer-api-changelog-rss-card";

const items = [
  { item_id: "i1", title: "New Users Endpoint", description: "Added /api/v2/users", category: "feature", version: "2.0" },
  { item_id: "i2", title: "Fixed auth bug", description: "Token validation fix", category: "fix", version: "2.0.1" },
];

describe("APIDeveloperAPIApiDeveloperApiChangelogRssCard", () => {
  it("shows changelog feed", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiChangelogRssCard items={items} appName="App" />);
    expect(container.textContent).toContain("Changelog Feed");
    expect(container.textContent).toContain("New Users Endpoint");
    expect(container.textContent).toContain("feature");
    expect(container.textContent).toContain("v2.0");
    expect(container.textContent).toContain("fix");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiChangelogRssCard items={[]} appName="App" />);
    expect(container.textContent).toContain("No changelog entries");
  });
});
