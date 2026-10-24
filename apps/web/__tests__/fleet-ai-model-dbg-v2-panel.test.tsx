import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelDbgV2Panel } from "@/components/fleet-ai-model-dbg-v2-panel";
describe("FleetAiModelDbgV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelDbgV2Panel debuggers={4} active={4} sessions={20000} breakpoints={500} resolved={480} />);
    expect(container.textContent).toContain("Model Debugger v2");
}); });
