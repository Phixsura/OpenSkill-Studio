"use client";

interface Feature { title: string; description: string; icon: string; }
interface CaseStudy { company: string; industry: string; quote: string; results: string; }
interface EnterprisePageLayoutProps { features: Feature[]; caseStudies: CaseStudy[];
  onContactSales: () => void; }

export function EnterprisePageLayout({ features, caseStudies, onContactSales }: EnterprisePageLayoutProps) {
  return (
    <div className="mx-auto max-w-5xl space-y-12">
      <div className="text-center">
        <h1 className="text-3xl font-bold">OpenSkill for Enterprise</h1>
        <p className="mt-2 text-lg text-gray-500">Scale your platform with enterprise-grade features</p>
        <button onClick={onContactSales} className="mt-4 rounded-lg bg-blue-600 px-8 py-3 text-sm font-semibold text-white">
          Contact Sales
        </button>
      </div>
      <div className="grid grid-cols-2 gap-6 sm:grid-cols-4">
        {features.map(f => (
          <div key={f.title} className="rounded-lg border border-gray-200 p-4 text-center dark:border-gray-700">
            <span className="text-2xl">{f.icon}</span>
            <h3 className="mt-2 font-semibold">{f.title}</h3>
            <p className="mt-1 text-xs text-gray-500">{f.description}</p>
          </div>
        ))}
      </div>
      {caseStudies.length > 0 && (
        <div>
          <h2 className="text-center text-2xl font-bold">Trusted by Leading Companies</h2>
          <div className="mt-6 grid gap-6 sm:grid-cols-2">
            {caseStudies.map(cs => (
              <div key={cs.company} className="rounded-xl bg-gray-50 p-6 dark:bg-gray-800">
                <p className="text-lg italic text-gray-600 dark:text-gray-400">&ldquo;{cs.quote}&rdquo;</p>
                <div className="mt-4">
                  <p className="font-semibold">{cs.company}</p>
                  <p className="text-xs text-gray-400">{cs.industry} · {cs.results}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
