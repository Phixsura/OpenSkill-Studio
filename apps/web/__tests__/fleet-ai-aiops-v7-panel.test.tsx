import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiAiopsV7Panel } from "@/components/fleet-ai-aiops-v7-panel";
describe("FleetAiAiopsV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiAiopsV7Panel systems={5} active={5} autoResolved={10000} anomalies={1000} toil={98} predAcc={99} />);
    expect(container.textContent).toContain("AIOps v7");
}); });
