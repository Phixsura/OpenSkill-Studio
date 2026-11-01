import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SvcChangelog } from "@/components/svc-changelog";
describe("SvcChangelog", () => {
  it("renders", () => {
    const { container } = render(
      <SvcChangelog totalChanges={3} versions={{ "2.0": [{ type: "feat", description: "Dark mode" }] }} />
    );
    expect(container.textContent).toContain("Changelog");
    expect(container.textContent).toContain("v2.0");
    expect(container.textContent).toContain("Dark mode");
  });
});
