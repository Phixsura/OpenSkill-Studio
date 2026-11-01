import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TokenScopeViewer } from "@/components/token-scope-viewer";

describe("TokenScopeViewer", () => {
  it("shows granted and inherited", () => {
    const { container } = render(
      <TokenScopeViewer name="CI Token" grantedScopes={["write"]} effectiveScopes={["write", "read"]} />
    );
    expect(container.textContent).toContain("CI Token");
    expect(container.textContent).toContain("write");
    expect(container.textContent).toContain("read");
    expect(container.textContent).toContain("Inherited");
  });
  it("no inherited when exact match", () => {
    const { container } = render(
      <TokenScopeViewer name="Token" grantedScopes={["read"]} effectiveScopes={["read"]} />
    );
    expect(container.textContent).not.toContain("Inherited");
  });
});
