import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { KeyScopePanel } from "@/components/key-scope-panel";
describe("KeyScopePanel", () => {
  it("renders", () => {
    const { container } = render(
      <KeyScopePanel keys={[
        { name: "ci-key", scopes: ["read", "deploy"], active: true, usage: 500 },
        { name: "old-key", scopes: ["read"], active: false, usage: 100 },
      ]} />
    );
    expect(container.textContent).toContain("API Key Scopes");
    expect(container.textContent).toContain("2 keys");
    expect(container.textContent).toContain("ci-key");
    expect(container.textContent).toContain("read");
    expect(container.textContent).toContain("deploy");
    expect(container.textContent).toContain("500 uses");
  });
});
