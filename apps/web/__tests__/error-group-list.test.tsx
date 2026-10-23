import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ErrorGroupList } from "@/components/error-group-list";

describe("ErrorGroupList", () => {
  it("renders groups", () => {
    const groups = [{ fingerprint: "abc", type: "TypeError", message: "x is undefined", count: 15, first_seen: "2026-01-01", last_seen: "2026-01-15" }];
    const { container } = render(<ErrorGroupList groups={groups} onSelect={vi.fn()} />);
    expect(container.textContent).toContain("TypeError");
    expect(container.textContent).toContain("15");
    expect(container.textContent).toContain("x is undefined");
  });
  it("empty state", () => {
    const { container } = render(<ErrorGroupList groups={[]} onSelect={vi.fn()} />);
    expect(container.textContent).toContain("No errors");
  });
  it("selects group", () => {
    const fn = vi.fn();
    const groups = [{ fingerprint: "xyz", type: "E", message: "M", count: 1, first_seen: "", last_seen: "" }];
    const { container } = render(<ErrorGroupList groups={groups} onSelect={fn} />);
    fireEvent.click(container.querySelector("li")!);
    expect(fn).toHaveBeenCalledWith("xyz");
  });
});
