import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { VersionBumpSelector } from "@/components/version-bump-selector";

describe("VersionBumpSelector", () => {
  it("renders bumps", () => {
    const { container } = render(
      <VersionBumpSelector currentVersion="1.2.3" onBump={vi.fn()} />
    );
    expect(container.textContent).toContain("Version Bump");
    expect(container.textContent).toContain("v1.2.3");
    expect(container.textContent).toContain("v1.2.4");
    expect(container.textContent).toContain("v1.3.0");
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("Patch");
    expect(container.textContent).toContain("Minor");
    expect(container.textContent).toContain("Major");
  });
});
