import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DataMaskingPreview } from "@/components/data-masking-preview";

describe("DataMaskingPreview", () => {
  const fields = [
    { key: "email", original: "alice@x.com", masked: "al***@x.com", type: "email" },
    { key: "phone", original: "1234567890", masked: "123****90", type: "phone" },
  ];
  it("renders", () => {
    const { container } = render(<DataMaskingPreview fields={fields} fieldsMasked={2} />);
    expect(container.textContent).toContain("Data Masking");
    expect(container.textContent).toContain("2 fields masked");
    expect(container.textContent).toContain("📧");
    expect(container.textContent).toContain("al***@x.com");
    expect(container.textContent).toContain("123****90");
  });
});
