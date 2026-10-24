import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CspBuilderPanel } from "@/components/csp-builder-panel";

describe("CspBuilderPanel", () => {
  const directives = { "default-src": ["'self'"], "script-src": ["'self'"] };
  it("renders CSP header and directives", () => {
    const { container } = render(
      <CspBuilderPanel header="default-src 'self'; script-src 'self'" directives={directives}
        warnings={["Missing frame-ancestors"]} directiveCount={2} />
    );
    expect(container.textContent).toContain("default-src");
    expect(container.textContent).toContain("script-src");
    expect(container.textContent).toContain("Missing frame-ancestors");
    expect(container.textContent).toContain("2 directives");
  });
});
