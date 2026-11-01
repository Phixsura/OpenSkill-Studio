import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiRuntimeAnalyticsV9Panel } from "@/components/fleet-api-runtime-analytics-v9-panel";
describe("FleetApiRuntimeAnalyticsV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiRuntimeAnalyticsV9Panel services={200} cpu={40} />);
    expect(container.textContent).toContain("Runtime Analytics v9");
}); });
