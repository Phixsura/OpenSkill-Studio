import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiClassifyPanel } from "@/components/fleet-ai-classify-panel";
describe("FleetAiClassifyPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiClassifyPanel classifiers={5} active={5} predictions={50000000} classes={1000} accuracy={98} />);
    expect(container.textContent).toContain("Classification");
}); });
