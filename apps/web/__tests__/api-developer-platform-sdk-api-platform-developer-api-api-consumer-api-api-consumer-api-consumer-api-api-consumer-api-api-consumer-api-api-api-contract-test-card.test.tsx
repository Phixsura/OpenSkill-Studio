import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-api-consumer-api-api-api-contract-test-card";

describe("ApiContractTestCard", () => {
  it("shows contracts", () => {
    const contracts = [{ id: "c1", endpoint: "/api/users", method: "GET", assertionCount: 3, lastResult: true }];
    const { container } = render(<Card contracts={contracts} appName="App" />);
    expect(container.textContent).toContain("API Contracts");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("3 assertions");
    expect(container.textContent).toContain("✅");
  });
  it("shows empty", () => {
    const { container } = render(<Card contracts={[]} appName="App" />);
    expect(container.textContent).toContain("No contracts defined");
  });
});
