import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { VersionCompareView } from "@/components/version-compare-view";

describe("VersionCompareView", () => {
  it("renders comparison", () => {
    const { container } = render(
      <VersionCompareView fromVersion="1.0" toVersion="2.0"
        added={["graphql", "sso"]} removed={["basic_api"]}
        unchanged={["auth", "webhooks"]} breaking={true} summary="+2 -1 =2" />
    );
    expect(container.textContent).toContain("Version Comparison");
    expect(container.textContent).toContain("1.0 → 2.0");
    expect(container.textContent).toContain("Breaking");
    expect(container.textContent).toContain("+ graphql");
    expect(container.textContent).toContain("- basic_api");
    expect(container.textContent).toContain("auth");
  });
});
