import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiVersionSelector } from "@/components/api-version-selector";

describe("ApiVersionSelector", () => {
  const versions = [
    { version: "v1", status: "deprecated", sunsetDate: "2026-06-01", released: "2024-01-01" },
    { version: "v2", status: "stable", sunsetDate: null, released: "2025-06-01" },
  ];
  it("renders versions", () => {
    const { container } = render(<ApiVersionSelector versions={versions} selected="v2" onSelect={vi.fn()} />);
    expect(container.textContent).toContain("v1");
    expect(container.textContent).toContain("deprecated");
    expect(container.textContent).toContain("v2");
    expect(container.textContent).toContain("stable");
  });
  it("selects version", () => {
    const fn = vi.fn();
    const { container } = render(<ApiVersionSelector versions={versions} selected="v2" onSelect={fn} />);
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith("v1");
  });
});
