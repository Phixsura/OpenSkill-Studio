import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { VersionBumpSelector } from "@/components/version-bump-selector";

describe("VersionBumpSelector", () => {
  it("shows versions", () => {
    const { container } = render(<VersionBumpSelector currentVersion="1.2.3" onSelect={vi.fn()} />);
    expect(container.textContent).toContain("1.2.4");
    expect(container.textContent).toContain("1.3.0");
    expect(container.textContent).toContain("2.0.0");
    expect(container.textContent).toContain("Current: 1.2.3");
  });
  it("calls onSelect", () => {
    const fn = vi.fn();
    const { container } = render(<VersionBumpSelector currentVersion="1.0.0" onSelect={fn} />);
    const btns = container.querySelectorAll("button");
    fireEvent.click(btns[1]); // minor
    expect(fn).toHaveBeenCalledWith("minor", "1.1.0");
  });
});
