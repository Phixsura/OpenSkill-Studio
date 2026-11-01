import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDataopsV7Panel } from "@/components/fleet-ai-dataops-v7-panel";
describe("FleetAiDataopsV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiDataopsV7Panel systems={4} active={4} pipelines={1000} datasets={10000} quality={99} freshness={2} />);
    expect(container.textContent).toContain("DataOps v7");
}); });
