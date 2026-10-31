import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetFirebasePanel } from "@/components/fleet-firebase-panel";
describe("FleetFirebasePanel", () => { it("renders", () => {
    const { container } = render(<FleetFirebasePanel projects={10} active={10} authUsers={2000000} firestoreDocs={50000000} storageGb={500} />);
    expect(container.textContent).toContain("Firebase");
}); });
