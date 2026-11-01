import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { InputSecurityBadge } from "@/components/input-security-badge";

describe("InputSecurityBadge", () => {
  it("all safe", () => {
    const checks = [{ name: "XSS", safe: true }, { name: "SQL Injection", safe: true }];
    const { container } = render(<InputSecurityBadge checks={checks} />);
    expect(container.textContent).toContain("Input Validated");
    expect(container.textContent).toContain("🛡️");
  });
  it("issues found", () => {
    const checks = [{ name: "XSS", safe: true }, { name: "SQL Injection", safe: false, details: "OR detected" }];
    const { container } = render(<InputSecurityBadge checks={checks} />);
    expect(container.textContent).toContain("Security Issues");
    expect(container.textContent).toContain("OR detected");
  });
});
