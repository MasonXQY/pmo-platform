import Layout from "../components/Layout";

export default function Dashboard() {
  return (
    <Layout>
      <h2 className="text-2xl font-semibold mb-4">Dashboard</h2>

      <div className="grid grid-cols-4 gap-6">
        <div className="bg-white p-4 shadow rounded">
          <p className="text-sm text-gray-500">Active Projects</p>
          <p className="text-2xl font-bold">--</p>
        </div>

        <div className="bg-white p-4 shadow rounded">
          <p className="text-sm text-gray-500">Projects at Risk</p>
          <p className="text-2xl font-bold text-red-500">--</p>
        </div>
      </div>
    </Layout>
  );
}
