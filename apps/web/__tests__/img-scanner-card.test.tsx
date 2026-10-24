import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ImgScannerCard } from "@/components/img-scanner-card";

describe("ImgScannerCard", () => {
  it("renders", () => {
    const { container } = render(
      <ImgScannerCard totalImages={3} passRate={67} totalVulns={7}
        results={[
          { image: "api:v3.0", sizeMb: 250, vulns: 2, critical: 0, high: 0, pass: true, issues: [] },
          { image: "old:v1", sizeMb: 800, vulns: 5, critical: 1, high: 2, pass: false, issues: ["Image too large"] },
        ]} />
    );
    expect(container.textContent).toContain("Image Scanner");
    expect(container.textContent).toContain("3 images");
    expect(container.textContent).toContain("67% pass");
    expect(container.textContent).toContain("api:v3.0");
    expect(container.textContent).toContain("old:v1");
    expect(container.textContent).toContain("Image too large");
  });
});
