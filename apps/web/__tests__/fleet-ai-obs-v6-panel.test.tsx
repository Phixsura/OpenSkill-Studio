import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiObsV6Panel } from "@/components/fleet-ai-obs-v6-panel";
describe("FleetAiObsV6Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiObsV6Panel stacks={5} active={5} pillars={5} dashboards={1000} alerts={5000} />);
    expect(container.textContent).toContain("Observability v6");
}); });
