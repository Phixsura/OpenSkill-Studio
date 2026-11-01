import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetBackupVaultV9Panel } from "@/components/fleet-backup-vault-v9-panel";
describe("FleetBackupVaultV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetBackupVaultV9Panel total={100} sizeGb={800} />);
    expect(container.textContent).toContain("Backup Vault v9");
}); });
