import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiFutureV8Panel } from "@/components/fleet-ai-future-v8-panel";
describe("FleetAiFutureV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiFutureV8Panel planners={3} active={3} capabilities={1000} research={500} prototypes={100} />);
    expect(container.textContent).toContain("Future v8");
}); });
