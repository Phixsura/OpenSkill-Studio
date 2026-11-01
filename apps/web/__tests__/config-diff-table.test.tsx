import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ConfigDiffTable } from "@/components/config-diff-table";

describe("ConfigDiffTable", () => {
  const rows = [
    { key: "PORT", values: { dev: "3000", prod: "3000" }, isMatch: true, missingIn: [] },
    { key: "DEBUG", values: { dev: "true", prod: "false" }, isMatch: false, missingIn: [] },
  ];
  it("renders diff table", () => {
    const { container } = render(
      <ConfigDiffTable rows={rows} environments={["dev", "prod"]} mismatches={1} inSync={false} />
    );
    expect(container.textContent).toContain("PORT");
    expect(container.textContent).toContain("DEBUG");
    expect(container.textContent).toContain("1 differences");
    expect(container.textContent).toContain("dev");
    expect(container.textContent).toContain("prod");
  });
});
