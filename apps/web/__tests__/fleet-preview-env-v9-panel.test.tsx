import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPreviewEnvV9Panel } from "@/components/fleet-preview-env-v9-panel";
describe("FleetPreviewEnvV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetPreviewEnvV9Panel running={10} expired={2} />);
    expect(container.textContent).toContain("Preview Env v9");
}); });
