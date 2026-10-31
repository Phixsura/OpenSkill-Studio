import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-token-exchange-card";

describe("TokenExchangeCard", () => {
  it("shows stats", () => {
    const { container } = render(<Card pendingCodes={3} totalExchanges={150} appName="App" />);
    expect(container.textContent).toContain("Token Exchange");
    expect(container.textContent).toContain("3");
    expect(container.textContent).toContain("150");
    expect(container.textContent).toContain("OAuth2");
  });
  it("shows zero", () => {
    const { container } = render(<Card pendingCodes={0} totalExchanges={0} appName="App" />);
    expect(container.textContent).toContain("Token Exchange");
  });
});
