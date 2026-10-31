import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import EndpointRegistryCard from "../src/components/api-developer-platform-sdk-consumer-api-endpoint-registry-card";

describe("EndpointRegistryCard", () => {
  it("renders title and endpoints", () => {
    const { container } = render(<EndpointRegistryCard />);
    expect(container.textContent).toContain("Endpoint Registry");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("/api/orders");
  });

  it("shows team count", () => {
    const { container } = render(<EndpointRegistryCard />);
    expect(container.textContent).toContain("4 endpoints");
    expect(container.textContent).toContain("3 teams");
  });
});
