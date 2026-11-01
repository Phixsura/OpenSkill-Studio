import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelDbgPanel } from "@/components/fleet-ai-model-dbg-panel";
describe("FleetAiModelDbgPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelDbgPanel debuggers={3} active={3} sessions={5000} issues={100} fixed={100} />);
    expect(container.textContent).toContain("Model Debugger");
}); });
