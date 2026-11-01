import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GeoRoutePanel } from "@/components/geo-route-panel";

describe("GeoRoutePanel", () => {
  it("renders", () => {
    const { container } = render(
      <GeoRoutePanel selectedRegion="eu-west" healthy={2} total={3}
        regions={[
          { name: "eu-west", endpoint: "eu.api.com", status: "healthy", distanceKm: 500 },
          { name: "us-east", endpoint: "us.api.com", status: "healthy", distanceKm: 6000 },
          { name: "ap-south", endpoint: "ap.api.com", status: "unhealthy", distanceKm: 8000 },
        ]} />
    );
    expect(container.textContent).toContain("Geo Routing");
    expect(container.textContent).toContain("eu-west");
    expect(container.textContent).toContain("2/3 healthy");
    expect(container.textContent).toContain("500km");
    expect(container.textContent).toContain("us.api.com");
  });
});
