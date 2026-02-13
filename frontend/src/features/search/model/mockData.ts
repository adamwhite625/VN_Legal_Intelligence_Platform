export interface LawItem {
  id: number;
  title: string;
  type: string;
  year: string;
  authority: string;
  description: string;
}

export const mockLaws: LawItem[] = [
  {
    id: 1,
    title: "Luật Doanh nghiệp 2020",
    type: "Luật",
    year: "2020",
    authority: "Quốc hội",
    description: "Quy định về thành lập và hoạt động doanh nghiệp",
  },
  {
    id: 2,
    title: "Nghị định 01/2021/NĐ-CP",
    type: "Nghị định",
    year: "2021",
    authority: "Chính phủ",
    description: "Hướng dẫn đăng ký doanh nghiệp",
  },
  {
    id: 3,
    title: "Luật Đầu tư 2020",
    type: "Luật",
    year: "2020",
    authority: "Quốc hội",
    description: "Quy định về hoạt động đầu tư kinh doanh",
  },
];
