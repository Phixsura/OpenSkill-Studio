import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CspPolicyEditor } from "@/components/csp-policy-editor";

const directives = [
  { name: "script-src", sources: ["'self'", "https://cdn.example.com", "'nonce-abc123'"] },
  { name: "img-src", sources: ["'self'", "data:"] },
];
const violations = { total: 5, byDirective: { "script-src": 3 }, topBlocked: { "https://evil.com/x.js": 3 } };

describe("CspPolicyEditor", () => {
  it("renders directives with source badges", () => {
    const { container } = render(<CspPolicyEditor directives={directives} violations={{ total: 0, byDirective: {}, topBlocked: {} }} strict />);
    expect(container.textContent).toContain("script-src");
    expect(container.textContent).toContain("cdn.example.com");
    expect(container.textContent).toContain("Strict Mode");
  });

  it("shows violations", () => {
    const { container } = render(<CspPolicyEditor directives={directives} violations={violations} strict />);
    expect(container.textContent).toContain("5 CSP Violations");
    expect(container.textContent).toContain("evil.com");
  });

  it("add source", () => {
    const fn = vi.fn();
    const { container } = render(<CspPolicyEditor directives={[]} violations={{ total: 0, byDirective: {}, topBlocked: {} }} strict onAddSource={fn} />);
    const input = container.querySelectorAll("input")[1];  // after checkbox
    fireEvent.change(input, { target: { value: "https://cdn.test.com" } });
    const addBtn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Add");
    if (addBtn) fireEvent.click(addBtn);
    expect(fn).toHaveBeenCalledWith("script-src", "https://cdn.test.com");
  });
});
