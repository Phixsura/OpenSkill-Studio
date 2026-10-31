import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ChangelogGenerator } from "@/components/changelog-generator";

describe("ChangelogGenerator", () => {
  const sections = [
    { type: "feat", label: "Features", icon: "✨", entries: [
      { type: "feat", scope: "auth", description: "Add SSO", icon: "✨" }
    ]},
  ];
  it("renders changelog", () => {
    const { container } = render(
      <ChangelogGenerator sections={sections} totalCommits={3} parsed={2}
        breaking={["API redesign"]} hasBreaking={true} />
    );
    expect(container.textContent).toContain("Generated Changelog");
    expect(container.textContent).toContain("Features");
    expect(container.textContent).toContain("Add SSO");
    expect(container.textContent).toContain("(auth)");
    expect(container.textContent).toContain("Breaking Changes");
    expect(container.textContent).toContain("API redesign");
  });
});
