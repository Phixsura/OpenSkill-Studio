import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-consumer-endpoint-api-changelog-aggregator-card";

describe("ChangelogAggregatorCard", () => {
  it("shows changelog", () => {
    const entries = [{ id: "e1", version: "2.0", type: "added", title: "OAuth2 Support", breaking: false }];
    const { container } = render(<Card entries={entries} totalEntries={10} breakingCount={1} versions={["2.0", "1.0"]} byType={{ added: 5, fixed: 3 }} appName="App" />);
    expect(container.textContent).toContain("Changelog");
    expect(container.textContent).toContain("OAuth2 Support");
    expect(container.textContent).toContain("added: 5");
    expect(container.textContent).toContain("1 breaking");
  });
  it("shows empty", () => {
    const { container } = render(<Card entries={[]} totalEntries={0} breakingCount={0} versions={[]} byType={{}} appName="App" />);
    expect(container.textContent).toContain("No changelog entries");
  });
});
