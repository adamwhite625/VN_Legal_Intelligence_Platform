import { useSearchStore } from "../model/searchStore";

export default function FilterPanel() {
  const { setFilter } = useSearchStore();

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Bộ lọc</h2>

      <select
        onChange={(e) => setFilter("type", e.target.value)}
        className="w-full p-2 border rounded"
      >
        <option value="">Loại văn bản</option>
        <option value="Luật">Luật</option>
        <option value="Nghị định">Nghị định</option>
      </select>

      <select
        onChange={(e) => setFilter("year", e.target.value)}
        className="w-full p-2 border rounded"
      >
        <option value="">Năm ban hành</option>
        <option value="2020">2020</option>
        <option value="2021">2021</option>
      </select>

      <select
        onChange={(e) => setFilter("authority", e.target.value)}
        className="w-full p-2 border rounded"
      >
        <option value="">Cơ quan ban hành</option>
        <option value="Quốc hội">Quốc hội</option>
        <option value="Chính phủ">Chính phủ</option>
      </select>
    </div>
  );
}
