import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReqAuditPanel } from "@/components/req-audit-panel";
describe("ReqAuditPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ReqAuditPanel total={5000} uniqueUsers={50}
        entries={[
          { userId: "u1", method: "GET", path: "/api/users", status: 200 },
          { userId: "u2", method: "POST", path: "/api/orders", status: 403 },
        ]} />
    );
    expect(container.textContent).toContain("Request Audit");
    expect(container.textContent).toContain("5,000 logged");
    expect(container.textContent).toContain("50 users");
    expect(container.textContent).toContain("u1");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("403");
  });
});
