import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDrV5Panel } from "@/components/fleet-ai-dr-v5-panel";
describe("FleetAiDrV5Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiDrV5Panel plans={3} active={3} rto={15} rpo={3} drills={12} regions={15} />);
    expect(container.textContent).toContain("AI DR v5");
}); });
