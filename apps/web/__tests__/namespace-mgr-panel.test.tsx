import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { NamespaceMgrPanel } from "@/components/namespace-mgr-panel";
describe("NamespaceMgrPanel", () => {
  it("renders", () => {
    const { container } = render(
      <NamespaceMgrPanel tenants={2}
        namespaces={[
          { name: "acme-prod", tenant: "acme", status: "active" },
          { name: "beta-prod", tenant: "beta", status: "active" },
        ]} />
    );
    expect(container.textContent).toContain("Namespaces");
    expect(container.textContent).toContain("2 namespaces");
    expect(container.textContent).toContain("2 tenants");
    expect(container.textContent).toContain("acme-prod");
    expect(container.textContent).toContain("acme");
  });
});
