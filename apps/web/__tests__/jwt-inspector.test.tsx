import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { JwtInspector } from "@/components/jwt-inspector";

describe("JwtInspector", () => {
  it("renders JWT", () => {
    const { container } = render(
      <JwtInspector valid={true} algorithm="HS256" expired={false}
        header={{ alg: "HS256", typ: "JWT" }}
        payload={{ sub: "user1", role: "admin" }}
        standardClaims={["sub"]} customClaims={["role"]} />
    );
    expect(container.textContent).toContain("JWT Inspector");
    expect(container.textContent).toContain("Valid");
    expect(container.textContent).toContain("HS256");
    expect(container.textContent).toContain("sub");
    expect(container.textContent).toContain("role");
  });
});
