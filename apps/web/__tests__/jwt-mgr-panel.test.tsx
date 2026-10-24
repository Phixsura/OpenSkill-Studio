import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { JwtMgrPanel } from "@/components/jwt-mgr-panel";
describe("JwtMgrPanel", () => {
  it("renders", () => {
    const { container } = render(
      <JwtMgrPanel activeCount={3}
        tokens={[
          { subject: "user-1", expiresIn: 3200, claims: ["admin", "read"] },
          { subject: "svc-api", expiresIn: 7200, claims: ["service"] },
        ]} />
    );
    expect(container.textContent).toContain("JWT Tokens");
    expect(container.textContent).toContain("3 active");
    expect(container.textContent).toContain("user-1");
    expect(container.textContent).toContain("admin, read");
  });
});
