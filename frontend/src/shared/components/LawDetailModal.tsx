import React from "react";

interface Props {
  open: boolean;
  onClose: () => void;
  data: any;
  loading?: boolean;
}

export default function LawDetailModal({
  open,
  onClose,
  data,
  loading,
}: Props) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="bg-white rounded-xl shadow max-w-3xl w-full max-h-[80vh] overflow-auto p-6">
        <div className="flex items-start justify-between">
          <h3 className="text-xl font-semibold">
            {data?.article_title || data?.law_name || "Law detail"}
          </h3>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-800"
          >
            Close
          </button>
        </div>

        {loading ? (
          <div className="mt-4">Loading...</div>
        ) : (
          <div className="mt-4 space-y-4 text-sm text-gray-800">
            {data?.summary && (
              <div className="italic text-gray-600">{data.summary}</div>
            )}
            <div
              dangerouslySetInnerHTML={{
                __html: data?.law_content || "<p>No content</p>",
              }}
            />
            {data?.origin_url && (
              <div className="mt-3 text-xs">
                <a
                  href={data.origin_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  View source document
                </a>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
