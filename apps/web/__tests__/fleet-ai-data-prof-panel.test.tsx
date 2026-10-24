import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDataProfPanel } from "@/components/fleet-ai-data-prof-panel";
describe("FleetAiDataProfPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDataProfPanel profilers={4} active={4} datasets={1000} columns={10000} anomalies={100} />);
    expect(container.textContent).toContain("Data Profiler");
}); });
