import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiVersionSelector } from "@/components/api-version-selector";

const versions = [
  { version: "v2", status: "active", changelog: ["New endpoints"] },
  { version: "v1", status: "deprecated", changelog: ["Legacy"] },
];

describe("ApiVersionSelector", () => {
  it("renders versions", () => {
    const { container } = render(<ApiVersionSelector versions={versions} selected="v2" />);
    expect(container.textContent).toContain("v2");
    expect(container.textContent).toContain("deprecated");
  });
  it("calls onSelect", () => {
    const fn = vi.fn();
    const { container } = render(<ApiVersionSelector versions={versions} selected="v2" onSelect={fn} />);
    const btns = container.querySelectorAll("button");
    fireEvent.click(btns[1]);
    expect(fn).toHaveBeenCalledWith("v1");
  });
});
