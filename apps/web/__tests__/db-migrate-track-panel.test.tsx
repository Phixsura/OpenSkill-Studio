import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DbMigrateTrackPanel } from "@/components/db-migrate-track-panel";

describe("DbMigrateTrackPanel", () => {
  it("renders", () => {
    const { container } = render(
      <DbMigrateTrackPanel applied={2} pending={1}
        migrations={[
          { version: "001", description: "Create users", applied: true, reversible: true },
          { version: "002", description: "Add email", applied: true, reversible: true },
          { version: "003", description: "Drop legacy", applied: false, reversible: false },
        ]} />
    );
    expect(container.textContent).toContain("Migrations");
    expect(container.textContent).toContain("2 applied");
    expect(container.textContent).toContain("1 pending");
    expect(container.textContent).toContain("001");
    expect(container.textContent).toContain("Create users");
    expect(container.textContent).toContain("irreversible");
  });
});
