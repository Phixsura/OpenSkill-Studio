import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { VersionCompareView } from "@/components/version-compare-view";

describe("VersionCompareView", () => {
  it("shows versions", () => {
    const { container } = render(<VersionCompareView v1="1.0" v2="2.0" added={["write:x"]} removed={[]} breaking={false} sandboxChanged={false} />);
    expect(container.textContent).toContain("v1.0 → v2.0");
    expect(container.textContent).toContain("write:x");
  });
});
