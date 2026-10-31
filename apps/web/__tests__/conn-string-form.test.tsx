import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ConnStringForm } from "@/components/conn-string-form";

describe("ConnStringForm", () => {
  it("renders form", () => {
    const { container } = render(
      <ConnStringForm uri="postgresql://admin:****@db:5432/mydb"
        masked="postgresql://admin:****@db:5432/mydb" engine="postgres"
        engines={["postgres", "mysql", "redis"]} onBuild={vi.fn()} />
    );
    expect(container.textContent).toContain("Connection String");
    expect(container.textContent).toContain("postgres");
    expect(container.textContent).toContain("mysql");
    expect(container.textContent).toContain("****");
  });
});
