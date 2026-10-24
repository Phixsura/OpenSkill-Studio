import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MigrationWizardUi } from "@/components/migration-wizard-ui";

describe("MigrationWizardUi", () => {
  it("renders wizard", () => {
    const onRun = vi.fn();
    const { container, getByText } = render(
      <MigrationWizardUi source="legacy" destination="new" completed={1} total={2} status="in_progress"
        onRunStep={onRun} steps={[
          { index: 0, dataType: "users", status: "completed", recordsMigrated: 1000, errors: 0 },
          { index: 1, dataType: "orders", status: "pending", recordsMigrated: 0, errors: 0 },
        ]} />
    );
    expect(container.textContent).toContain("Data Migration");
    expect(container.textContent).toContain("legacy → new");
    expect(container.textContent).toContain("1/2");
    expect(container.textContent).toContain("1,000 records");
    fireEvent.click(getByText("Migrate"));
    expect(onRun).toHaveBeenCalledWith(1);
  });
});
