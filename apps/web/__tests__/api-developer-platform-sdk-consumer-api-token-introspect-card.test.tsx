import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import TokenIntrospectCard from "../src/components/api-developer-platform-sdk-consumer-api-token-introspect-card";

describe("TokenIntrospectCard", () => {
  it("renders title and tokens", () => {
    const { container } = render(<TokenIntrospectCard />);
    expect(container.textContent).toContain("Token Introspection");
    expect(container.textContent).toContain("tok_a1b2c3");
    expect(container.textContent).toContain("access");
    expect(container.textContent).toContain("refresh");
  });

  it("shows active count", () => {
    const { container } = render(<TokenIntrospectCard />);
    expect(container.textContent).toContain("2/3 tokens active");
    expect(container.textContent).toContain("revoked");
  });
});
