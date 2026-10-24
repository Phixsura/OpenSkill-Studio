import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetClickhousePanel } from "@/components/fleet-clickhouse-panel";
describe("FleetClickhousePanel", () => { it("renders", () => {
    const { container } = render(<FleetClickhousePanel shards={4} healthy={4} totalRows={5000000000} qps={2000} />);
    expect(container.textContent).toContain("ClickHouse");
    expect(container.textContent).toContain("2000 qps");
}); });
