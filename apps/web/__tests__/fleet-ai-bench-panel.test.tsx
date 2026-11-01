import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiBenchPanel } from "@/components/fleet-ai-bench-panel";
describe("FleetAiBenchPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiBenchPanel benches={5} active={5} models={200} suites={50} runs={20000} />);
    expect(container.textContent).toContain("AI Benchmark");
}); });
