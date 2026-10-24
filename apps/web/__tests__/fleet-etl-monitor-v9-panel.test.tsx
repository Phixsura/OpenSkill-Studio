import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetEtlMonitorV9Panel } from "@/components/fleet-etl-monitor-v9-panel";
describe("FleetEtlMonitorV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetEtlMonitorV9Panel jobs={100} rows={10000000} />);
    expect(container.textContent).toContain("ETL Monitor v9");
}); });
