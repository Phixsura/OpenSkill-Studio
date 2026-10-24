import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetIamPanel } from "@/components/fleet-iam-panel";
describe("FleetIamPanel", () => { it("renders", () => {
    const { container } = render(<FleetIamPanel total={100} withMfa={95} unusedKeys={5} admins={3} secure={false} />);
    expect(container.textContent).toContain("IAM");
    expect(container.textContent).toContain("5 unused");
}); });
