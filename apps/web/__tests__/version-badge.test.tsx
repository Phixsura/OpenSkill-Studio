import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { VersionBadge } from "@/components/version-badge";

describe("VersionBadge", () => {
  it("renders stable version", () => {
    const { container } = render(<VersionBadge version="2.1.0" isStable={true} prerelease={null} />);
    expect(container.textContent).toContain("v2.1.0");
    expect(container.textContent).toContain("Stable");
  });
  it("renders prerelease", () => {
    const { container } = render(<VersionBadge version="3.0.0-beta.1" isStable={false} prerelease="beta.1" />);
    expect(container.textContent).toContain("beta.1");
  });
  it("bump buttons", () => {
    const fn = vi.fn();
    const { container } = render(<VersionBadge version="1.0.0" isStable={true} prerelease={null} showBump onBump={fn} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "minor")!);
    expect(fn).toHaveBeenCalledWith("minor");
  });
});
