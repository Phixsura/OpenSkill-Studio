import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DataMaskingReport } from "@/components/data-masking-report";

describe("DataMaskingReport", () => {
  it("renders masked output", () => {
    const { container } = render(
      <DataMaskingReport masked="Email: al••••@example.com" redactions={1} typesFound={["email"]} />
    );
    expect(container.textContent).toContain("al••••@example.com");
    expect(container.textContent).toContain("1 redaction");
    expect(container.textContent).toContain("email");
    expect(container.textContent).toContain("📧");
  });
});
