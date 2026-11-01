import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DataMaskingPreview } from "@/components/data-masking-preview";

describe("DataMaskingPreview", () => {
  it("renders masked data", () => {
    const { container } = render(
      <DataMaskingPreview fieldsMasked={1} sensitiveFields={["ssn"]}
        records={[
          { name: "Alice", ssn: "***-**-6789" },
          { name: "Bob", ssn: "***-**-1234" },
        ]} />
    );
    expect(container.textContent).toContain("Data Masking");
    expect(container.textContent).toContain("1 fields masked");
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("***-**-6789");
  });
});
