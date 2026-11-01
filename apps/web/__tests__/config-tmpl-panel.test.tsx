import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ConfigTmplPanel } from "@/components/config-tmpl-panel";
describe("ConfigTmplPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ConfigTmplPanel templateName="app.conf" complete={false}
        usedVars={["HOST"]} missingVars={["DB_PORT"]} />
    );
    expect(container.textContent).toContain("Config Template");
    expect(container.textContent).toContain("1 missing");
    expect(container.textContent).toContain("app.conf");
    expect(container.textContent).toContain("Used: HOST");
    expect(container.textContent).toContain("Missing: DB_PORT");
  });
});
