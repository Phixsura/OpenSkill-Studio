import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ConfigDriftViewer } from "@/components/config-drift-viewer";

describe("ConfigDriftViewer", () => {
  it("renders drifts", () => {
    const { container } = render(
      <ConfigDriftViewer hasDrift={true} totalKeys={5} envNames={["production", "staging"]}
        drifts={[
          { key: "debug", values: { production: false, staging: true }, environments: 2 },
          { key: "db_host", values: { production: "prod-db", staging: "stg-db" }, environments: 2 },
        ]} />
    );
    expect(container.textContent).toContain("Config Drift");
    expect(container.textContent).toContain("2/5 keys drifted");
    expect(container.textContent).toContain("debug");
    expect(container.textContent).toContain("db_host");
    expect(container.textContent).toContain("prod-db");
    expect(container.textContent).toContain("stg-db");
  });
});
