import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetBigqueryPanel } from "@/components/fleet-bigquery-panel";
describe("FleetBigqueryPanel", () => { it("renders", () => {
    const { container } = render(<FleetBigqueryPanel datasets={20} tables={1000} storageTb={200} queries={50000} bytesProcessed={500} />);
    expect(container.textContent).toContain("BigQuery");
    expect(container.textContent).toContain("1000 tables");
}); });
