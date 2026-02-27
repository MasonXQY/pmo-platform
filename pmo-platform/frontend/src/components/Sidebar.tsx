export default function Sidebar() {
  return (
    <div className="w-64 bg-white shadow-md p-6">
      <h1 className="text-xl font-bold mb-6">PMO Platform</h1>
      <nav className="space-y-3">
        <a href="/" className="block hover:text-blue-600">Dashboard</a>
        <a href="/projects" className="block hover:text-blue-600">Projects</a>
      </nav>
    </div>
  );
}
