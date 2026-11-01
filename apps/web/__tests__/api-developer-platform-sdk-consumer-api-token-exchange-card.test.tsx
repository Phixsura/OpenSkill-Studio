import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import TokenExchangeCard from "../src/components/api-developer-platform-sdk-consumer-api-token-exchange-card";

describe("TokenExchangeCard", () => {
  it("renders title and stats", () => {
    const { container } = render(<TokenExchangeCard />);
    expect(container.textContent).toContain("Token Exchange");
    expect(container.textContent).toContain("24");
    expect(container.textContent).toContain("Exchanges");
  });

  it("shows audiences", () => {
    const { container } = render(<TokenExchangeCard />);
    expect(container.textContent).toContain("auth-service");
    expect(container.textContent).toContain("billing-service");
  });
});
