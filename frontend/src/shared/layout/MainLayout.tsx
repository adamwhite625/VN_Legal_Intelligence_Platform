import type { ReactNode } from "react";
import Navbar from "./Navbar";
import Sidebar from "./Sidebar";

interface Props {
  children: ReactNode;
}

export default function MainLayout({ children }: Props) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      <Navbar />

      <div className="flex mt-16">
        <Sidebar />

        <main className="flex-1 p-8">{children}</main>
      </div>
    </div>
  );
}
