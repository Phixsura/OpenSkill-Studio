import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AccessTokenPanel } from "@/components/access-token-panel";

describe("AccessTokenPanel", () => {
  it("renders", () => {
    const { container } = render(
      <AccessTokenPanel activeCount={5} revokedCount={2}
        tokens={[
          { preview: "osk_abc...xyz", subject: "user-1", scopes: ["read", "write"], expiresIn: 3200 },
        ]} />
    );
    expect(container.textContent).toContain("Access Tokens");
    expect(container.textContent).toContain("5 active");
    expect(container.textContent).toContain("2 revoked");
    expect(container.textContent).toContain("osk_abc...xyz");
    expect(container.textContent).toContain("user-1");
    expect(container.textContent).toContain("read, write");
  });
});
