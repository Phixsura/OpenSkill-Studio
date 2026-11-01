import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRuntimeMetricsV9Panel } from "@/components/fleet-runtime-metrics-v9-panel";
describe("FleetRuntimeMetricsV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetRuntimeMetricsV9Panel apps={50} memory={800} />);
    expect(container.textContent).toContain("Runtime Metrics v9");
}); });
