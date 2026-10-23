import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TokenUsageMeter } from "@/components/token-usage-meter";

describe("TokenUsageMeter", () => {
  it("renders usage", () => {
    const { container } = render(
      <TokenUsageMeter totalConsumed={50000} activeKeys={25} avgPerKey={2000}
        topEndpoints={[
          { endpoint: "/api/users", count: 15000 },
          { endpoint: "/api/data", count: 10000 },
        ]} />
    );
    expect(container.textContent).toContain("Token Usage");
    expect(container.textContent).toContain("50,000");
    expect(container.textContent).toContain("25");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("15000");
  });
});
