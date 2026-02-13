import { useSearchStore } from "../model/searchStore";
import { Link } from "react-router-dom";

export default function ResultList() {
  const { results, keyword } = useSearchStore();

  if (results.length === 0) {
    return <div>Không tìm thấy kết quả</div>;
  }

  return (
    <div className="space-y-4">
      {results.map((law) => (
        <Link key={law.id} to={`/law/${law.id}?keyword=${keyword}`}>
          <div className="bg-white p-4 rounded-xl shadow hover:shadow-md transition cursor-pointer">
            <h3 className="font-semibold text-lg">{law.title}</h3>
            <p className="text-sm text-gray-600">
              {law.authority} - {law.year}
            </p>
            <p className="mt-2 text-gray-700 text-sm">{law.description}</p>
          </div>
        </Link>
      ))}
    </div>
  );
}
