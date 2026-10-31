import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ServiceMeshCard from "../src/components/api-developer-platform-sdk-consumer-api-service-mesh-card";

describe("ServiceMeshCard", () => {
  it("renders title and nodes", () => {
    const { container } = render(<ServiceMeshCard />);
    expect(container.textContent).toContain("Service Mesh");
    expect(container.textContent).toContain("Auth");
    expect(container.textContent).toContain("Payments");
  });

  it("shows links and circuit info", () => {
    const { container } = render(<ServiceMeshCard />);
    expect(container.textContent).toContain("circuit open");
    expect(container.textContent).toContain("4 services");
    expect(container.textContent).toContain("1 open circuits");
  });
});
