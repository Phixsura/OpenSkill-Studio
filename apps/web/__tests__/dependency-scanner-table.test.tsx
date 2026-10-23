import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DependencyScannerTable } from "@/components/dependency-scanner-table";

describe("DependencyScannerTable", () => {
  it("renders deps", () => {
    const { container } = render(
      <DependencyScannerTable healthDisplay="25%" actionRequired={true} results={[
        { name: "lodash", current: "4.17.20", latest: "4.17.21", status: "vulnerable",
          vulnerabilities: [{ id: "CVE-2021-23337", severity: "high" }], updateAvailable: true },
        { name: "next", current: "15.0.0", latest: "15.0.0", status: "up_to_date",
          vulnerabilities: [], updateAvailable: false },
      ]} />
    );
    expect(container.textContent).toContain("Dependencies");
    expect(container.textContent).toContain("25%");
    expect(container.textContent).toContain("Action needed");
    expect(container.textContent).toContain("lodash");
    expect(container.textContent).toContain("vulnerable");
    expect(container.textContent).toContain("up to date");
  });
});
