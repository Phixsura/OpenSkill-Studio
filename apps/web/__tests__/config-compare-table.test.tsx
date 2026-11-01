import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ConfigCompareTable } from "@/components/config-compare-table";

describe("ConfigCompareTable", () => {
  it("renders diffs", () => {
    const { container } = render(
      <ConfigCompareTable environments={["dev", "prod"]} sameCount={1} diffCount={2} identical={false}
        diffs={[
          { key: "debug", values: { dev: true, prod: false } },
          { key: "db_host", values: { dev: "localhost", prod: "prod-db" } },
        ]} />
    );
    expect(container.textContent).toContain("Config Comparison");
    expect(container.textContent).toContain("1 same");
    expect(container.textContent).toContain("2 different");
    expect(container.textContent).toContain("debug");
    expect(container.textContent).toContain("localhost");
    expect(container.textContent).toContain("prod-db");
  });
});
