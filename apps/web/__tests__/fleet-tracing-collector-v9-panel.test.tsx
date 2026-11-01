import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTracingCollectorV9Panel } from "@/components/fleet-tracing-collector-v9-panel";
describe("FleetTracingCollectorV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetTracingCollectorV9Panel collectors={8} sps={50000} />);
    expect(container.textContent).toContain("Tracing Collector v9");
}); });
