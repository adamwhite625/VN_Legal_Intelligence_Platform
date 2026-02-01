export default function ChatLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="h-screen w-screen flex overflow-hidden bg-muted/30">
      {children}
    </div>
  );
}
