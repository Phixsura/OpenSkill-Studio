import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetBinaryArtifactV9Panel } from "@/components/fleet-binary-artifact-v9-panel";
describe("FleetBinaryArtifactV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetBinaryArtifactV9Panel artifacts={500} downloads={100000} />);
    expect(container.textContent).toContain("Binary Artifact v9");
}); });
