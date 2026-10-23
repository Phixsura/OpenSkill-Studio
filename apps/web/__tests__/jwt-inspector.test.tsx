import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { JwtInspector } from "@/components/jwt-inspector";

describe("JwtInspector", () => {
  it("renders input", () => {
    const { container } = render(<JwtInspector onDecode={vi.fn()} />);
    expect(container.textContent).toContain("JWT Inspector");
    expect(container.querySelector("textarea")).toBeTruthy();
  });
});
