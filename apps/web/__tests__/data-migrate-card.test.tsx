import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DataMigrateCard } from "@/components/data-migrate-card";

describe("DataMigrateCard", () => {
  it("renders", () => {
    const { container } = render(
      <DataMigrateCard source="old-db" target="new-db" totalRows={250000} estimatedMinutes={9}
        steps={[
          { table: "orders", rows: 200000, estimatedMinutes: 4, strategy: "bulk" },
          { table: "users", rows: 50000, estimatedMinutes: 5, strategy: "streaming" },
        ]} />
    );
    expect(container.textContent).toContain("Data Migration");
    expect(container.textContent).toContain("old-db");
    expect(container.textContent).toContain("new-db");
    expect(container.textContent).toContain("250,000 rows");
    expect(container.textContent).toContain("orders");
    expect(container.textContent).toContain("bulk");
    expect(container.textContent).toContain("streaming");
  });
});
