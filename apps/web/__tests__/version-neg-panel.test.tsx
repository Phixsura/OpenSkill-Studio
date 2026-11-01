import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { VersionNegPanel } from "@/components/version-neg-panel";
describe("VersionNegPanel", () => {
  it("renders", () => {
    const { container } = render(
      <VersionNegPanel latest="v3" active={["v2", "v3"]} deprecated={["v1"]} />
    );
    expect(container.textContent).toContain("API Versions");
    expect(container.textContent).toContain("latest: v3");
    expect(container.textContent).toContain("2 active");
    expect(container.textContent).toContain("1 deprecated");
    expect(container.textContent).toContain("v2");
    expect(container.textContent).toContain("v1");
  });
});
