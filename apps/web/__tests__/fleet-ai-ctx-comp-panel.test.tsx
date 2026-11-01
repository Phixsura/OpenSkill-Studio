import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCtxCompPanel } from "@/components/fleet-ai-ctx-comp-panel";
describe("FleetAiCtxCompPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiCtxCompPanel compressors={3} active={3} compressions={20000000} ratio={5} quality={99} />);
    expect(container.textContent).toContain("Context Compressor");
}); });
