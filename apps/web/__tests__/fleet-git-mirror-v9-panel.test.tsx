import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGitMirrorV9Panel } from "@/components/fleet-git-mirror-v9-panel";
describe("FleetGitMirrorV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetGitMirrorV9Panel mirrors={10} synced={10} />);
    expect(container.textContent).toContain("Git Mirror v9");
}); });
