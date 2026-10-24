import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DataRedactPanel } from "@/components/data-redact-panel";
describe("DataRedactPanel", () => {
  it("renders", () => {
    const { container } = render(
      <DataRedactPanel redactedFields={1500} patternsActive={3} samplesProcessed={10000} />
    );
    expect(container.textContent).toContain("Data Redaction");
    expect(container.textContent).toContain("3 patterns");
    expect(container.textContent).toContain("10,000 processed");
    expect(container.textContent).toContain("1,500");
  });
});
