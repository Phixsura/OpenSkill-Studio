"use client";

interface SurveyInfo { survey_id: string; title: string; question_count: number; response_count: number; }
interface Props { surveys: SurveyInfo[]; appName: string; }

export default function APIDeveloperFeedbackSurveyCard({ surveys, appName }: Props) {
  const totalResponses = surveys.reduce((s, sv) => s + sv.response_count, 0);
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📝 Feedback Surveys</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{surveys.length} surveys · {totalResponses} responses</span>
      </div>
      {surveys.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No surveys</p>
      ) : (
        <div className="space-y-1">
          {surveys.map((s) => (
            <div key={s.survey_id} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{s.title}</span>
              <span className="text-gray-400">{s.question_count}Q · {s.response_count} responses</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
