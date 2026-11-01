import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ChangelogRssWidget } from "@/components/changelog-rss-widget";

describe("ChangelogRssWidget", () => {
  it("renders feed", () => {
    const { container } = render(
      <ChangelogRssWidget title="App Changelog" feedUrl="/rss" itemCount={2}
        entries={[
          { title: "v2.0", description: "Major update", date: "2024-01-01" },
          { title: "v1.5", description: "Bug fixes", date: "2023-12-01" },
        ]} />
    );
    expect(container.textContent).toContain("App Changelog");
    expect(container.textContent).toContain("2 entries");
    expect(container.textContent).toContain("v2.0");
    expect(container.textContent).toContain("Major update");
    expect(container.textContent).toContain("RSS");
  });
});
