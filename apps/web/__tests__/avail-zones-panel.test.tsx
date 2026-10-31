import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AvailZonesPanel } from "@/components/avail-zones-panel";

describe("AvailZonesPanel", () => {
  it("renders", () => {
    const { container } = render(
      <AvailZonesPanel totalZones={3} healthy={2} unhealthy={1} regions={2}
        byRegion={{ "us-east-1": 2, "eu-west-1": 1 }} multiAz={true} allHealthy={false} />
    );
    expect(container.textContent).toContain("Availability Zones");
    expect(container.textContent).toContain("3 zones");
    expect(container.textContent).toContain("2 regions");
    expect(container.textContent).toContain("1 unhealthy");
    expect(container.textContent).toContain("us-east-1: 2 AZs");
    expect(container.textContent).toContain("Multi-AZ");
  });
});
