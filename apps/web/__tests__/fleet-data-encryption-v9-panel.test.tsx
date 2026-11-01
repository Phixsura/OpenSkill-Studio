import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDataEncryptionV9Panel } from "@/components/fleet-data-encryption-v9-panel";
describe("FleetDataEncryptionV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetDataEncryptionV9Panel resources={500} atRest={500} />);
    expect(container.textContent).toContain("Data Encryption v9");
}); });
