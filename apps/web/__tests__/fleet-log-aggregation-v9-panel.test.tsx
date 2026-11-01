import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetLogAggregationV9Panel } from "@/components/fleet-log-aggregation-v9-panel";
describe("FleetLogAggregationV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetLogAggregationV9Panel collectors={10} eps={50000} />);
    expect(container.textContent).toContain("Log Aggregation v9");
}); });
