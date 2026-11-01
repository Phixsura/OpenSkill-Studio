import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-explorer-card";

describe("ConsumerApiExplorerCard", () => {
  it("shows categories", () => {
    const categories = [{ name: "users", endpoints: [{ id: "e1", method: "GET", path: "/api/users", summary: "List", authRequired: true }] }];
    const { container } = render(<Card categories={categories} totalEndpoints={1} appName="App" />);
    expect(container.textContent).toContain("API Explorer");
    expect(container.textContent).toContain("users");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("/api/users");
  });
  it("shows empty", () => {
    const { container } = render(<Card categories={[]} totalEndpoints={0} appName="App" />);
    expect(container.textContent).toContain("No endpoints");
  });
});
