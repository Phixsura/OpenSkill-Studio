"use client";

interface CertInfo { certId: string; name: string; description: string; passingScore: number; questions: number; }
interface CertResult { certId: string; score: number; passed: boolean; certificateCode: string; expiresAt: string; }

export function DeveloperCertPanel({ certs, results, onTakeExam }: {
  certs: CertInfo[]; results: CertResult[];
  onTakeExam?: (certId: string) => void;
}) {
  const passedIds = new Set(results.filter(r => r.passed).map(r => r.certId));

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">🎓 Developer Certifications</h2>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {certs.map((c) => {
          const result = results.find(r => r.certId === c.certId && r.passed);
          return (
            <div key={c.certId} className={`rounded-xl border-2 p-4 ${passedIds.has(c.certId) ? "border-green-400" : "dark:border-gray-700"}`}>
              <div className="flex items-center justify-between mb-2">
                <span className="font-bold text-sm">{c.name}</span>
                {result && <span className="text-xs bg-green-600 text-white px-2 py-0.5 rounded-full">✓ Certified</span>}
              </div>
              <p className="text-xs text-gray-500 mb-2">{c.description}</p>
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-400">{c.questions} questions · {c.passingScore}% to pass</span>
                {!result && (
                  <button onClick={() => onTakeExam?.(c.certId)}
                    className="text-xs bg-blue-600 text-white px-3 py-1 rounded-lg">Take Exam</button>
                )}
              </div>
              {result && <div className="text-xs text-gray-400 mt-1">Score: {result.score}% · Code: {result.certificateCode}</div>}
            </div>
          );
        })}
      </div>
    </div>
  );
}
