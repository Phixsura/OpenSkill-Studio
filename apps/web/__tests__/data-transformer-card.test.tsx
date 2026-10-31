import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import DataTransformerCard from "../src/components/data-transformer-card";

const rules = [
  { rule_id: "r1", rule_type: "rename" as const, source_field: "name", target_field: "full_name" },
  { rule_id: "r2", rule_type: "filter" as const, source_field: "password", target_field: "" },
  { rule_id: "r3", rule_type: "default" as const, source_field: "role", target_field: "role" },
  { rule_id: "r4", rule_type: "compute" as const, source_field: "", target_field: "display_name" },
];

describe("DataTransformerCard", () => {
  it("renders header and ruleset id", () => {
    const { container } = render(
      <DataTransformerCard rulesetId="rs-1" rules={rules} appName="My App" />,
    );
    expect(container.textContent).toContain("Transform Rules");
    expect(container.textContent).toContain("rs-1");
  });

  it("shows rule count", () => {
    const { container } = render(
      <DataTransformerCard rulesetId="rs-1" rules={rules} appName="App" />,
    );
    expect(container.textContent).toContain("4 rules");
  });

  it("renders rule types", () => {
    const { container } = render(
      <DataTransformerCard rulesetId="rs-1" rules={rules} appName="App" />,
    );
    expect(container.textContent).toContain("rename");
    expect(container.textContent).toContain("filter");
    expect(container.textContent).toContain("default");
    expect(container.textContent).toContain("compute");
  });

  it("shows field names", () => {
    const { container } = render(
      <DataTransformerCard rulesetId="rs-1" rules={rules} appName="App" />,
    );
    expect(container.textContent).toContain("name");
    expect(container.textContent).toContain("full_name");
  });

  it("shows arrow for renames", () => {
    const { container } = render(
      <DataTransformerCard rulesetId="rs-1" rules={rules} appName="App" />,
    );
    expect(container.textContent).toContain("→");
  });

  it("shows empty state", () => {
    const { container } = render(<DataTransformerCard rulesetId="rs-1" rules={[]} appName="App" />);
    expect(container.textContent).toContain("No rules defined");
  });
});
