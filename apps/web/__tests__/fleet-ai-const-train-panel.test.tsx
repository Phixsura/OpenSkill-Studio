import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiConstTrainPanel } from "@/components/fleet-ai-const-train-panel";
describe("FleetAiConstTrainPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiConstTrainPanel trainers={3} active={3} principles={100} revisions={500000} alignment={98} />);
    expect(container.textContent).toContain("Constitutional Training");
}); });
