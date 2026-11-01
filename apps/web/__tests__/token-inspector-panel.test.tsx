import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TokenInspectorPanel } from "@/components/token-inspector-panel";

describe("TokenInspectorPanel", () => {
  it("renders", () => {
    const { container } = render(<TokenInspectorPanel onDecode={vi.fn(() => ({ claims: {}, expired: false, scopes: [] }))} />);
    expect(container.textContent).toContain("Token Inspector");
    expect(container.querySelector("textarea")).toBeTruthy();
    expect(container.textContent).toContain("Decode");
  });
  it("decode", () => {
    const fn = vi.fn(() => ({ claims: { sub: "u1", iss: "test" }, expired: false, scopes: ["read"] }));
    const { container } = render(<TokenInspectorPanel onDecode={fn} />);
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Decode")!);
    expect(fn).toHaveBeenCalled();
    expect(container.textContent).toContain("u1");
  });
});
