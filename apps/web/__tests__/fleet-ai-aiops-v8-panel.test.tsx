import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiAiopsV8Panel } from "@/components/fleet-ai-aiops-v8-panel";
describe("FleetAiAiopsV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiAiopsV8Panel systems={5} active={5} auto={200000} anomalies={5000} predAcc={99} toil={99} />);
    expect(container.textContent).toContain("AIOps v8");
}); });
