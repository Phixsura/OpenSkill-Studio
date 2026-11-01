import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ScopeAuditCard from "../src/components/api-developer-platform-sdk-consumer-api-scope-audit-card";

describe("ScopeAuditCard", () => {
  it("renders title and keys", () => {
    const { container } = render(<ScopeAuditCard />);
    expect(container.textContent).toContain("Scope Audit");
    expect(container.textContent).toContain("key_prod_1");
    expect(container.textContent).toContain("key_admin");
  });

  it("shows recommendations", () => {
    const { container } = render(<ScopeAuditCard />);
    expect(container.textContent).toContain("optimal");
    expect(container.textContent).toContain("reduce scopes");
    expect(container.textContent).toContain("1/3 keys optimal");
  });
});
