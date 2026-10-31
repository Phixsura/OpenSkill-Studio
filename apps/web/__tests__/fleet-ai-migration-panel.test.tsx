import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiMigrationPanel } from "@/components/fleet-ai-migration-panel";
describe("FleetAiMigrationPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiMigrationPanel migrations={10} running={2} completed={7} failed={1} dataGb={2000} />);
    expect(container.textContent).toContain("AI Migration");
}); });
