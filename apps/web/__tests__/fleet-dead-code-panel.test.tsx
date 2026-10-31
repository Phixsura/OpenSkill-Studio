import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDeadCodePanel } from "@/components/fleet-dead-code-panel";
describe("FleetDeadCodePanel", () => { it("renders", () => {
    const { container } = render(<FleetDeadCodePanel totalFiles={500} deadFiles={10} deadLoc={500} clean={false} />);
    expect(container.textContent).toContain("Dead Code");
    expect(container.textContent).toContain("10 dead files");
}); });
