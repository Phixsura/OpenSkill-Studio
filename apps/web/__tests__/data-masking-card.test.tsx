import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import DataMaskingCard from "../src/components/data-masking-card";

const rules = [
  { field: "password", strategy: "full" as const, visible_chars: 0 },
  { field: "email", strategy: "partial" as const, visible_chars: 4 },
  { field: "ssn", strategy: "hash" as const, visible_chars: 0 },
  { field: "notes", strategy: "redact" as const, visible_chars: 0 },
];

describe("DataMaskingCard", () => {
  it("renders header", () => {
    const { container } = render(
      <DataMaskingCard rulesetId="rs1" rules={rules} appName="My App" />,
    );
    expect(container.textContent).toContain("Data Masking");
    expect(container.textContent).toContain("rs1");
  });

  it("shows rule count", () => {
    const { container } = render(<DataMaskingCard rulesetId="rs1" rules={rules} appName="App" />);
    expect(container.textContent).toContain("4 rules");
  });

  it("renders fields and strategies", () => {
    const { container } = render(<DataMaskingCard rulesetId="rs1" rules={rules} appName="App" />);
    expect(container.textContent).toContain("password");
    expect(container.textContent).toContain("Full mask");
    expect(container.textContent).toContain("email");
    expect(container.textContent).toContain("Partial");
    expect(container.textContent).toContain("Hash");
    expect(container.textContent).toContain("Redact");
  });

  it("shows visible chars for partial", () => {
    const { container } = render(<DataMaskingCard rulesetId="rs1" rules={rules} appName="App" />);
    expect(container.textContent).toContain("show 4 chars");
  });

  it("shows empty state", () => {
    const { container } = render(<DataMaskingCard rulesetId="rs1" rules={[]} appName="App" />);
    expect(container.textContent).toContain("No masking rules");
  });
});
