import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetInfluxdbPanel } from "@/components/fleet-influxdb-panel";
describe("FleetInfluxdbPanel", () => { it("renders", () => {
    const { container } = render(<FleetInfluxdbPanel instances={3} healthy={3} series={30000000} writesPerSec={1500000} />);
    expect(container.textContent).toContain("InfluxDB");
}); });
