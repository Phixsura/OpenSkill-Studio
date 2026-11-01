import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiEvalHarnessPanel } from "@/components/fleet-ai-eval-harness-panel";
describe("FleetAiEvalHarnessPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiEvalHarnessPanel harnesses={5} active={5} benchmarks={100} runs={50000} avgScore={95.2} />);
    expect(container.textContent).toContain("AI Eval Harness");
}); });
