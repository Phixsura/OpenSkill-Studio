import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ScopeCheckerDisplay } from "@/components/scope-checker-display";

describe("ScopeCheckerDisplay", () => {
  it("renders allowed", () => {
    const { container } = render(
      <ScopeCheckerDisplay allowed={true} required="read" granted={["write"]}
        effective={["read", "write"]} reason="scope_granted" />
    );
    expect(container.textContent).toContain("Scope Check");
    expect(container.textContent).toContain("Allowed");
    expect(container.textContent).toContain("read");
    expect(container.textContent).toContain("write");
  });

  it("renders denied", () => {
    const { container } = render(
      <ScopeCheckerDisplay allowed={false} required="delete" granted={["read"]}
        effective={["read"]} reason="insufficient_scope" />
    );
    expect(container.textContent).toContain("Denied");
  });
});
