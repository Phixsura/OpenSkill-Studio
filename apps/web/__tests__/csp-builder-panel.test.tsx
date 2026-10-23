import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CspBuilderPanel } from "@/components/csp-builder-panel";

describe("CspBuilderPanel", () => {
  it("renders", () => {
    const directives = { "default-src": ["'self'"], "script-src": ["'self'"] };
    const { container } = render(
      <CspBuilderPanel headerValue="default-src 'self'; script-src 'self'" directives={directives}
        securityScore={100} warnings={[]} onUpdate={vi.fn()} />
    );
    expect(container.textContent).toContain("Content Security Policy");
    expect(container.textContent).toContain("100/100");
    expect(container.textContent).toContain("default-src");
  });
  it("shows warnings", () => {
    const { container } = render(
      <CspBuilderPanel headerValue="x" directives={{}} securityScore={40}
        warnings={["unsafe-inline detected"]} onUpdate={vi.fn()} />
    );
    expect(container.textContent).toContain("⚠️ unsafe-inline detected");
    expect(container.textContent).toContain("40/100");
  });
});
