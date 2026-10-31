import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SdkQuickstartTabs } from "@/components/sdk-quickstart-tabs";

describe("SdkQuickstartTabs", () => {
  it("renders tabs", () => {
    const { container, getByText } = render(
      <SdkQuickstartTabs tabs={[
        { language: "typescript", install: "npm install @openskill/sdk", code: "const client = new OpenSkill()", hasInstall: true },
        { language: "python", install: "pip install openskill", code: "client = OpenSkill()", hasInstall: true },
      ]} />
    );
    expect(container.textContent).toContain("typescript");
    expect(container.textContent).toContain("npm install");
    expect(container.textContent).toContain("OpenSkill");
    fireEvent.click(getByText(/python/));
    expect(container.textContent).toContain("pip install");
  });
});
