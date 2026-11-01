import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import EndpointMapCard from "../src/components/api-developer-platform-sdk-consumer-api-endpoint-map-card";

describe("EndpointMapCard", () => {
  it("renders title and nodes", () => {
    const { container } = render(<EndpointMapCard />);
    expect(container.textContent).toContain("Endpoint Map");
    expect(container.textContent).toContain("Users API");
    expect(container.textContent).toContain("PostgreSQL");
  });

  it("shows edges and counts", () => {
    const { container } = render(<EndpointMapCard />);
    expect(container.textContent).toContain("calls");
    expect(container.textContent).toContain("4 nodes");
    expect(container.textContent).toContain("3 edges");
  });
});
