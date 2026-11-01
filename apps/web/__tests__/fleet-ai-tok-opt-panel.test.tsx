import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiTokOptPanel } from "@/components/fleet-ai-tok-opt-panel";
describe("FleetAiTokOptPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiTokOptPanel optimizers={4} active={4} optimized={50000000} tokensSaved={20000000000} savings={40} />);
    expect(container.textContent).toContain("Token Optimizer");
}); });
