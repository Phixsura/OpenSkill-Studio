import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelCompilePanel } from "@/components/fleet-ai-model-compile-panel";
describe("FleetAiModelCompilePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelCompilePanel compilers={3} active={3} models={500} speedup={4} targets={6} />);
    expect(container.textContent).toContain("Model Compiler");
}); });
