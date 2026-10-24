import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiBenchV2Panel } from "@/components/fleet-ai-bench-v2-panel";
describe("FleetAiBenchV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiBenchV2Panel benches={4} active={4} models={500} tasks={200} entries={1000} />);
    expect(container.textContent).toContain("Benchmark v2");
}); });
